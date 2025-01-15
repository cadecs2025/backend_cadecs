from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,  # Generates access & refresh tokens
    TokenRefreshView,  # Refreshes access token
)
from .views import DashboardView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('dashboard/', DashboardView.as_view()),
]