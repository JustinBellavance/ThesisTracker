from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("upload/", views.upload_docx, name="upload_docx"),
    path('account/', include('allauth.urls')),
    path("signup/", views.signup_view, name="signup"),
    path("profile/", views.profile, name="profile"),
    path('load-contribution-calendars', views.load_contribution_calendars, name='load_contribution_calendars'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)