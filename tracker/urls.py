from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("upload/", views.upload_docx, name="upload_docx"),
    path('accounts/', include('allauth.urls')),
]