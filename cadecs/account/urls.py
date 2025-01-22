from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,  # Generates access & refresh tokens
    TokenRefreshView,  # Refreshes access token
)
# from .views import DashboardView
from django.conf import settings
from django.conf.urls.static import static
from .views import OrganizationListView,OrganizationView,RegionView



urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('organization-listing/', OrganizationListView.as_view()),
    path('organization/', OrganizationView.as_view()),
    path('region/', RegionView.as_view()),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)