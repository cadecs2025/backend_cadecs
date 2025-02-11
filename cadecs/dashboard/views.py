from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from account.models import Organization, UserProfile



class DashboardView(APIView):
    permission_classes = [IsAuthenticated] 

    def get(self,request):                    
            
            total_user = UserProfile.objects.filter(is_active=True).count()
            total_org = Organization.objects.filter(is_deleted=False).count()
            
            dict_data = {'total_user':total_user,'total_org': total_org}
            
            resp = {
                'results': dict_data,            
                'resultCode': '1',
                'resultDescription': f'Get dashboard details.'
            }
            return Response(resp, status=status.HTTP_200_OK)
