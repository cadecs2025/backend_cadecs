from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,  # Generates access & refresh tokens
    TokenRefreshView,  # Refreshes access token
)
# from .views import DashboardView
from django.conf import settings
from django.conf.urls.static import static
from .views import *
from .CustomJWTSerializers import CustomTokenObtainPairSerializer

urlpatterns = [
    #done
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    #done
    path('organization-listing/', OrganizationListView.as_view()),
    path('organization/', OrganizationView.as_view()),
    path('organization-dropdown/', OrganizationDropDownView.as_view()),
    path('organization/<int:pk>/', OrganizationView.as_view()),
    
    #done
    path('region/', RegionView.as_view()),
    
    path('create-user/', UserProfileView.as_view()),
    path('create-user/<int:pk>/', UserProfileView.as_view()),
    path('user-listing/', UserProfileListView.as_view()),
    
    #done
    path('organization-type-listing/', OrganizationTypeListView.as_view()),
    path('organization-type/', OrganizationTypeView.as_view()),
    path('organization-type/<int:pk>/', OrganizationTypeView.as_view()),
    
    path('media/', MediaFileListView.as_view(), name='media-list-create'),
    path('menu-listing/', MenuListView.as_view(), name='menu-list-create'),
    
    #done
    path('roles/', RoleAPIView.as_view(), name='role-list-create'),
    path('roles/<int:pk>/', RoleAPIView.as_view(), name='role-detail'),
    path('roles-listing/', RoleListView.as_view())
    
]

# if settings.DEBUG:
    # urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)