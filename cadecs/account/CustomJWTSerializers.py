
from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import UserDetails

# User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        organization = UserDetails.objects.filter(user=token.get('user_id')).first()

        if not organization:
            organization_name = 'cadecs'
            role = "Admin"
        else:
            organization_name= organization.organization.organization_name
            role = organization.role.name

        print(f"organization: {organization}",flush=True)

        # Add extra fields to the token
        token['role'] = role # Assuming `role` is a field on your User model
        token['email'] = user.email
        token['organization'] = organization_name

        return token