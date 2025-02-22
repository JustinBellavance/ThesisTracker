from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import default_storage
from datetime import datetime, timedelta
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm  # Or your custom form
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib import messages


from .forms import CustomSignupForm
import plotly.graph_objs as go
from docx import Document
import json


import os

from .models import Thesis, CustomUser

from django.http import JsonResponse

@login_required
def upload_docx(request):
    if request.method == "POST" and request.FILES.get("docx_file"):
        uploaded_file = request.FILES["docx_file"]

        if not uploaded_file.name.endswith(".docx"):
            return JsonResponse({"error": "Invalid file type. Please upload a .docx file."}, status=400)

        temp_file_path = default_storage.save(uploaded_file.name, uploaded_file)

        try:
            doc = Document(temp_file_path)
            word_count = sum(len(run.text.split()) for paragraph in doc.paragraphs for run in paragraph.runs)
            
            previous_thesis = Thesis.objects.order_by('-upload_date').first()

            word_diff = word_count - previous_thesis.total_words if previous_thesis else word_count
            

            Thesis.objects.create(
                username=request.user.username,
                total_words=word_count,
                word_change=word_diff,
            )

            message = f"File uploaded successfully! Current word count: {word_count}. Difference from last upload: {word_diff} words."

            return JsonResponse({"message": message})

        except Exception as e:
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    return JsonResponse({"error": "No file uploaded."}, status=400)


def load_contribution_calendars(request):
    """ Returns a batch of contribution calendars """
    offset = int(request.GET.get("offset", 0))  # Get current batch index
    limit = 5  # Load 5 calendars at a time
    
    username = request.user.username if request.user.is_authenticated else None

    # Get all distinct usernames (excluding the logged-in user if authenticated)
    users = Thesis.objects.values_list("username", flat=True).distinct()

    # Exclude the logged-in user's username if they are authenticated
    if username:
        users = users.exclude(username=username)

    # Slice the list for pagination
    users = users[offset:offset + limit]
    
    calendars = []

    for user in users:
        heatmap_data, date_list, tooltip_text = generate_heatmap_data(user)

        week_labels = [(date_list[i * 7].strftime("%b %d")) for i in range(53)]
        day_labels = ["Sun  ", "Mon  ", "Tue  ", "Wed  ", "Thu  ", "Fri  ", "Sat  "]

        fig = go.Figure(
            data=go.Heatmap(
                z=heatmap_data,
                colorscale=[
                    [0.0, "#DDDDDD"],  
                    [0.5, "#28B463"],  
                    [1.0, "#1D8348"]  
                ],
                zmin=0,  # Ensure None values are not considered
                zmax=max((max([val for val in row if val is not None], default=0)) for row in heatmap_data) or 1,
                x=week_labels,
                y=day_labels,
                xgap=1,
                ygap=1,
                text=tooltip_text,
                hoverinfo="text"
            )
        )

        fig.update_layout(
            xaxis={"visible": False, "showticklabels": False},  
            yaxis={"autorange": "reversed", "scaleanchor": "x"}, 
            margin={'t': 0, 'b': 0, 'l': 10, 'r': 0},
            paper_bgcolor="white", 
            plot_bgcolor="white",    
            dragmode=False,
        )

        fig.update_traces(showscale=False)

        calendars.append({
            "username": user,
            "university": CustomUser.objects.filter(username=user).values_list("university", flat=True).first() or "Unknown University",
            "thesis_title" : CustomUser.objects.filter(username=user).values_list("thesis_title", flat=True).first() or "Unknown Thesis Title",
            "graph": json.dumps(fig.to_dict(), cls=DjangoJSONEncoder)
        })

    return JsonResponse({"calendars": calendars})




def generate_heatmap_data(username):
    today = datetime.now().date()
        
    # Align start_date to the most recent Sunday
    start_date = today - timedelta(days=365)
        
    while start_date.weekday() != 6:  # 6 is Sunday
        start_date -= timedelta(days=1)
        
    date_list = [start_date + timedelta(days=i) for i in range(365 + (start_date.weekday() - (5 - today.weekday()) ))]
    
    word_counts_by_date = {
        thesis.upload_date.date(): thesis.word_change 
        for thesis in Thesis.objects.filter(username=username)
    }

    heatmap_data = [[None] * 53 for _ in range(7)]
    tooltip_text = [[""] * 53 for _ in range(7)]

    for date in date_list:

        week_num = ((date - start_date).days) // 7
        day_of_week = date.weekday()
        
        # sunday first
        day_of_week += 1
        if day_of_week == 7:
            day_of_week = 0
            
        word_count = word_counts_by_date.get(date, 0)

        heatmap_data[day_of_week][week_num] = word_count
        tooltip_text[day_of_week][week_num] = f"{date.strftime('%b %d %Y')}: {word_count} words"
    
    last_column = [heatmap_data[row][week_num] for row in range(7)]
        
    missing_days = sum(1 for v in last_column if v is not None)
    
    # make first column aligned with rest
    for i in range(missing_days):
        heatmap_data[i][0] = None  # Fill first N spots in first column with None
        tooltip_text[i][0] = None

    return heatmap_data, date_list, tooltip_text


def index(request):
    if not request.user.username:
        return render(request, "index.html")

    username = request.user.username
    heatmap_data, date_list, tooltip_text = generate_heatmap_data(username)

    week_labels = [(date_list[i * 7].strftime("%b %d")) for i in range(53)]
    day_labels = ["Sun  ", "Mon  ", "Tue  ", "Wed  ", "Thu  ", "Fri  ", "Sat  "]

    fig = go.Figure(
        data=go.Heatmap(
            z=heatmap_data,
            colorscale=[
                [0.0, "#DDDDDD"],  
                [0.5, "#28B463"],  
                [1.0, "#1D8348"]  
            ],
            zmin=0,  # Ensure None values are not considered
            zmax=max((max([val for val in row if val is not None], default=0)) for row in heatmap_data) or 1,
            x=week_labels,
            y=day_labels,
            xgap=1,
            ygap=1,
            text=tooltip_text,
            hoverinfo="text"
        )
    )

    fig.update_layout(
        xaxis={"visible": False, "showticklabels": False},  
        yaxis={"autorange": "reversed", "scaleanchor": "x"}, 
        margin={'t': 0, 'b': 0, 'l': 10, 'r': 0},
        paper_bgcolor="white", 
        plot_bgcolor="white",    
        dragmode=False,
    )

    fig.update_traces(showscale=False)
    
    user = request.user
    missing_info = not user.thesis_title or not user.university
    
    context = {
        "graph": json.dumps(fig.to_dict(), cls=DjangoJSONEncoder),
        "config": json.dumps({"displayModeBar": False}, cls=DjangoJSONEncoder),
        "has_missing_info": missing_info
    }
    


    return render(request, "index.html", context)


def login(request):
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            # Custom login logic here
            from django.contrib.auth import authenticate, login
            user = authenticate(request, username=form.cleaned_data['login'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = CustomLoginForm()
    return render(request, "account/login.html", {'form': form})

@login_required
def profile(request):
    user = request.user  # Get the logged-in user (CustomUser instance)
    
    if request.method == "POST":
        user = request.user
        user.username = request.POST.get("username", user.username)
        user.email = request.POST.get("email", user.email)
        user.university = request.POST.get("university", user.university)
        user.thesis_title = request.POST.get("thesis_title", user.thesis_title)
        user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("profile")  # Redirect to avoid form resubmission
    
    missing_info = not user.thesis_title or not user.university

    return render(request, "profile.html", {"user": user, "has_missing_info" : missing_info})  # Pass user data to the template

def signup_view(request):
    if request.method == "POST":
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            form.save()  # Create the user
            return redirect('login')  # Redirect to login page after signup
    else:
        form = CustomSignupForm()

    return render(request, 'signup.html', {'form': form})