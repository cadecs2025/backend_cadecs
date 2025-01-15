from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

# Create your views here.


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        table_lists = []                 
        resp = {
            'results': table_lists,            
            'resultCode': '1',
            'resultDescription': 'Dashboard View'
        }
        return Response(resp, status=status.HTTP_200_OK)