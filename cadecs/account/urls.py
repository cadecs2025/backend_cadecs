from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,  # Generates access & refresh tokens
    TokenRefreshView,  # Refreshes access token
)
# from .views import DashboardView
from django.conf import settings
from django.conf.urls.static import static
from .views import *



urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('organization-listing/', OrganizationListView.as_view()),
    path('organization/', OrganizationView.as_view()),
    path('organization-dropdown/', OrganizationDropDownView.as_view()),
    path('organization/<int:pk>/', OrganizationView.as_view()),
    path('region/', RegionView.as_view()),
    path('organization-type/', OrganizationTypeView.as_view()),
    path('create-user/', UserProfileView.as_view()),
    path('create-user/<int:pk>/', UserProfileView.as_view()),
    path('user-listing/', UserProfileListView.as_view()),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)