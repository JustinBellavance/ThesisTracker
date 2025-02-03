from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import default_storage
from datetime import datetime, timedelta
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder

import plotly.graph_objs as go
from docx import Document
import json


import os

from .models import Thesis

@login_required
def upload_docx(request):
    if request.method == "POST" and request.FILES.get("docx_file"):
        uploaded_file = request.FILES["docx_file"]

        if not uploaded_file.name.endswith(".docx"):
            return HttpResponse("Invalid file type. Please upload a .docx file.", status=400)

        temp_file_path = default_storage.save(uploaded_file.name, uploaded_file)

        try:
            doc = Document(temp_file_path)
            word_count = sum(len(paragraph.text.split()) for paragraph in doc.paragraphs)

            previous_thesis = Thesis.objects.order_by('-upload_date').first()

            if previous_thesis:
                word_diff = word_count - previous_thesis.word_change
            else:
                word_diff = word_count 

            Thesis.objects.create(
                name = uploaded_file.name,
                username=request.user.username,
                word_change=word_diff,
            )

            message = f"File uploaded successfully! Word count: {word_count}. Difference from previous upload: {word_diff} words."

        except Exception as e:
            message = f"An error occurred while processing the file: {str(e)}"

        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

        return HttpResponse(message)

    return HttpResponse("No file uploaded.", status=400)

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
        day_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        fig = go.Figure(
            data=go.Heatmap(
                z=heatmap_data,
                colorscale=[
                    [0.0, "#DDDDDD"],  
                    [0.01, "#D6EAF8"],  
                    [0.5, "#5DADE2"],  
                    [1.0, "#154360"]  
                ],
                zmin=0,
                zmax=max(max(row) for row in heatmap_data) or 1,
                x=week_labels,
                y=day_labels,
                xgap=2,
                ygap=2,
                text=tooltip_text,
                hoverinfo="text"
            )
        )

        fig.update_layout(
            xaxis={"visible": False, "showticklabels": False},  
            margin={'t': 20, 'b': 0, 'l': 50, 'r': 50},
            yaxis={"autorange": "reversed"}
        )
        fig.update_traces(showscale=False)

        calendars.append({
            "username": user,
            "graph": json.dumps(fig.to_dict(), cls=DjangoJSONEncoder)
        })

    return JsonResponse({"calendars": calendars})


def generate_heatmap_data(username):
    today = datetime.now().date()
    start_date = today - timedelta(days=364)

    date_list = [start_date + timedelta(days=i) for i in range(365)]
    word_counts_by_date = {thesis.upload_date.date(): thesis.word_change 
                           for thesis in Thesis.objects.filter(username=username)}

    heatmap_data = [[0] * 53 for _ in range(7)]
    tooltip_text = [[""] * 53 for _ in range(7)]  # Tooltip text array

    for date in date_list:
        week_num = (date - start_date).days // 7
        day_of_week = date.weekday()
        word_count = word_counts_by_date.get(date, 0)

        heatmap_data[day_of_week][week_num] = word_count
        tooltip_text[day_of_week][week_num] = f"{date.strftime('%b %d')}: {word_count} words"

    return heatmap_data, date_list, tooltip_text

def index(request):
    if not request.user.username:
        return render(request, "index.html")

    username = request.user.username
    heatmap_data, date_list, tooltip_text = generate_heatmap_data(username)

    week_labels = [(date_list[i * 7].strftime("%b %d")) for i in range(53)]
    day_labels = ["Sat", "Sun", "Mon", "Tue", "Wed", "Thu", "Fri"]

    fig = go.Figure(
        data=go.Heatmap(
            z=heatmap_data,
            colorscale=[  # Custom color scale
                [0, "#DDDDDD"],  # Light grey for 0 values
                [0.1, "#D6EAF8"],  
                [0.5, "#5DADE2"],  
                [1, "#154360"]  # Dark blue for high values
            ],
            zmin=0,
            x=week_labels,
            y=day_labels,
            xgap=2,
            ygap=2,
            text=tooltip_text,  # Assign custom tooltip text
            hoverinfo="text"  # Ensure only text is shown on hover
        )
    )

    fig.update_layout(
        xaxis={"visible": False, "showticklabels": False},  
        margin={'t': 0, 'b': 0, 'l': 50, 'r': 50},
        yaxis={"autorange": "reversed"}
    )

    fig.update_traces(showscale=False)

    context = {
        "graph": json.dumps(fig.to_dict(), cls=DjangoJSONEncoder),
        "config": json.dumps({"displayModeBar": False}, cls=DjangoJSONEncoder),
    }

    return render(request, "index.html", context)

def login(request):
    return render(request, "account/login.html")

def signup(request):
    return render(request, "account/signup.html")
