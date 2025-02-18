from django.urls import path, include
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.conf import settings

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("upload/", views.upload_docx, name="upload_docx"),
    path('account/', include('allauth.urls')),
    path("signup/", views.signup_view, name="signup"),
    path("profile/", views.profile, name="profile"),
    path('load-contribution-calendars', views.load_contribution_calendars, name='load_contribution_calendars'),
    path("password_reset/", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)