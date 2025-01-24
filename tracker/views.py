from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import default_storage
from datetime import datetime, timedelta
import plotly.graph_objs as go
from docx import Document
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.decorators import login_required

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

def generate_heatmap_data(username):
    today = datetime.now().date()
    start_date = today - timedelta(days=365)
    date_list = [start_date + timedelta(days=i) for i in range(366)]

    word_counts_by_date = {}

    thesis_entries = Thesis.objects.filter(username=username)

    for thesis in thesis_entries:
        date_only = thesis.upload_date.date()
        word_counts_by_date[str(date_only)] = thesis.word_change

    week_data = [[] for _ in range(7)]  
    for date in date_list:
        weekday = date.weekday() 
        value = word_counts_by_date.get(str(date), 0)  
        week_data[weekday].append(value)

    return week_data, date_list

def index(request):
    
    if not request.user.username:
        return render(request, "index.html")
        
    username=request.user.username

    week_data, date_list = generate_heatmap_data(username)

    pconf = {
        "displayModeBar": False,  
    }

    fig = go.Figure(
        data=go.Heatmap(
            z=week_data,
            colorscale="Blues",
            xgap=2,
            ygap=2,
            x=[date.strftime("%b %d") for date in date_list[:53]],  
            y=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],  
        )
    )
    fig.update_layout(
        xaxis={"visible": False, "showticklabels": False},  
        margin={'t': 0, 'b': 0, 'l' : 100, 'r' : 100}, 
        yaxis={
                "scaleanchor": "x",
                "autorange": "reversed",
              },
    )

    fig.update_traces(showscale=False)  
    graph = fig.to_dict()
    
    context = {
        "graph": json.dumps(graph, cls=DjangoJSONEncoder),
        "config": json.dumps(pconf, cls=DjangoJSONEncoder),
    }
    
    return render(request, "index.html", context)

def login(request):
    return render(request, "account/login.html")

def signup(request):
    return render(request, "account/signup.html")
