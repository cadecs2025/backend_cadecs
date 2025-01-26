import json
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import OrganizationSerializer
from .models import Organization
from utils.pagination import GenericPagination
from utils.custom_exception import ResponseError
from assets.dropdown import organization_type



class RegionView(APIView):
    def get(self,request):      

        search = request.query_params.get('search', None) 
        with open('USCities.json', 'r') as file:
            filtered_data = data = json.load(file)  # Parse the JSON file into a Python dictionary  
        
        if search:
            filtered_data = [
                item for item in data
                if search.lower() in item['city'].lower() or search.lower() in item['state'].lower() or search.lower() in item['county'].lower()
            ]       

        paginator = GenericPagination()  
        paginated_data = paginator.paginate_queryset(filtered_data, request) 
        
        return paginator.get_paginated_response(paginated_data) 
    
class OrganizationTypeView(APIView):
    def get(self,request):  
        resp = {
                "results": organization_type,                
                "resultCode": "1"
            }
        return Response(resp, status=status.HTTP_200_OK)  


class OrganizationView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated] 

    def get(self,request,pk=None): 
        try:
            org_data = Organization.objects.get(pk=pk)
        except:
            raise ResponseError("Invalid primary key. Please input valid primary key.")
        else:   
            org_serializers = OrganizationSerializer(org_data)
            resp = {
                'results': org_serializers.data,            
                'resultCode': '1',
                'resultDescription': f'Get organization details by id.'
            }
            return Response(resp, status=status.HTTP_200_OK)
    
    def post(self, request):           
        user = self.request.user          
        context={'created_by':user}
        orgs_ser = OrganizationSerializer(data=request.data,context=context)       
        
        if orgs_ser.is_valid():
            orgs_ser.save()
            resp = {
                "results": "Requested Organization added successfully",
                "resultDescription": "Requested Organization added successfully",
                "resultCode": "1"
            }
            return Response(resp, status=status.HTTP_200_OK)
        else:
            org_name = request.data.get('organization_name') 
            ser_key = list(orgs_ser.errors.keys())[0]
            ser_val = ', '.join(orgs_ser.errors.get(ser_key))
            raise ResponseError(f"{ser_val}",
                                    f"Attempted to create organization {org_name} but raised error {ser_key} {ser_val}") 
        
    def patch(self,request,pk=None):        
        try:
            org_data = Organization.objects.get(pk=pk)
        except:
            raise ResponseError("Organization id not found",f"Attempt to organization but id not found.")
        else:    

            print(f"org_data: {org_data}",flush=True)
            print(f"request.data: {request.data}",flush=True)

            orgs_ser = OrganizationSerializer(org_data,data=request.data,partial=True)

            if orgs_ser.is_valid(): 
                print(f"serializers is valid: ",flush=True)
                orgs_ser.save()                
            else:            
                ser_key = list(orgs_ser.errors.keys())[0]
                ser_val = ', '.join(orgs_ser.errors.get(ser_key))          
                raise ResponseError(f"{ser_val}",
                                    f"Attempted to update organizations {org_data.organization_name} but raised error {ser_key} {ser_val}") 


            resp = {
                'results': f"Organization {org_data.organization_name} updated successfully",
                'resultCode': '1',
                'resultDescription': f"Organization {org_data.organization_name} updated successfully",
                
            }
            return Response(resp, status=status.HTTP_200_OK)     
    

        

class OrganizationListView(ListAPIView):
    queryset = Organization.objects.all().order_by("-id")
    serializer_class = OrganizationSerializer
    filter_backends = [OrderingFilter, SearchFilter]
    pagination_class = GenericPagination
    ordering_fields = ["organization_id","organization_name", "organization_type","registered_year","city","state","county","zip_code","cin"]
    search_fields = ["organization_id","organization_name", "organization_type","registered_year","city","state","county","zip_code","cin"]
        