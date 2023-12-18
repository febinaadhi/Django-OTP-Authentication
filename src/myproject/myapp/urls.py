# myapp/urls.py
from django.urls import path
from .views import UserRegistrationAPIView, TOTPRegistrationView, LoginAPIView

urlpatterns = [
    path('api/register/', UserRegistrationAPIView.as_view(), name='api-register'),
    path('api/totp/register/<int:device_id>/', TOTPRegistrationView.as_view(), name='totp-registration'),
    path('api/login/', LoginAPIView.as_view(), name='api-login'),
    # Add other URLs for your app as needed
]

