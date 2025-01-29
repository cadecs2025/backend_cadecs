import json
import re
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import *
from .models import Organization, UserProfile, create_user_details
from utils.pagination import GenericPagination
from utils.custom_exception import ResponseError
from assets.dropdown import organization_type
from utils.custom_exception import ValidationError
from utils.common_validators import FieldValidator


fieldvalidator = FieldValidator()



class RegionView(APIView):
    def get(self,request):      

        search = request.query_params.get('search', None) 
        with open('region.json', 'r') as file:
            filtered_data = json.load(file)  # Parse the JSON file into a Python dictionary 


            
        # if search:
        #     filtered_data = [
        #         item for item in data
        #         if search.lower() in item['city'].lower() or search.lower() in item['state'].lower() or search.lower() in item['county'].lower()
        #     ]       

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

class OrganizationDropDownView(APIView):
    permission_classes = [IsAuthenticated] 

    def get(self,request):        
            org_data = Organization.objects.all()        
            org_serializers = OrganizationDropDownSerializer(org_data,many=True)
            resp = {
                'results': org_serializers.data,            
                'resultCode': '1',
                'resultDescription': f'Get organization drop down details.'
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

    def delete(self,request,pk=None):
        payload = request.data
        del_reason = payload.get('del_reason')
        valid_reason = fieldvalidator.field_length_validator('del_reason', del_reason)
        if not valid_reason:
            raise ValidationError('Sorry, delete reason lenght must be between 3 to 200 character',
                                      "Attempted deleting organization but delete organization length was invalid")        
        
        try:
            organization = Organization.objects.get(pk=pk)            
        except Exception as e:
            raise ResponseError("Sorry, Organization Details not found",
                                f"Attempted to delete organization. Organization doesnot exist") 
        else:    
            organization_id = organization.organization_id
            print(f"organization_id: {organization_id}",flush=True)
            # DeleteUser.objects.create(widget_name=widget_name,
            #                             del_reason=del_reason,
            #                             deleted_by=request.user.email) 
            # X_AxisChartDetails.objects.filter(widget_id = pk).delete()
            # Y_AxisChartDetails.objects.filter(widget_id = pk).delete()            
            organization_id.is_deleted = True
            organization_id.save()
        
            resp = {
                'resultDescription': f"Organization {organization_id} is deleted Successfully",
                'resultCode': '1',
                "actionPerformed": f"""Organization {organization_id} has
                                            been deleted successfully.""",
            }
            return Response(resp, status=status.HTTP_200_OK)  
    

        

class OrganizationListView(ListAPIView):
    queryset = Organization.objects.filter(is_deleted=False).order_by("-id")
    serializer_class = OrganizationSerializer
    filter_backends = [OrderingFilter, SearchFilter]
    pagination_class = GenericPagination
    ordering_fields = ["organization_id","organization_name", "organization_type","registered_year","city","state","county","zip_code","cin"]
    search_fields = ["organization_id","organization_name", "organization_type","registered_year","city","state","county","zip_code","cin"]



class UserProfileView(APIView):
    permission_classes = ([IsAuthenticated])
    
    def post(self, request):
        resume =  request.data.get('resume',None)
        image = request.data.get('image',None)
        created_by = self.request.user.email
        email = request.data.get('email',None)
        password = request.data.get('password',None)
        username = request.data.get('username',None)
        first_name = request.data.get('first_name',None)
        last_name = request.data.get('last_name',None)
        is_active = request.data.get('is_active',True)
        phone_number = request.data.get('phone_number',None)
        alt_contact_number = request.data.get('alt_contact_number',None)
        address = request.data.get('address',None)
        city = request.data.get('city',None)
        state = request.data.get('state',None)
        country = request.data.get('country',None)
        zip_code = request.data.get('zip_code',None)
        gender = request.data.get('gender',None)
        nationality = request.data.get('nationality',None)
        organization = request.data.get('organization',None)

        if not email:
            resp = {
                    'errorMessage': "This email is already in use, please try another",
                    'resultCode': '0',
                    'resultDescription': "This email is already in use, please try another",
                    "actionPerformed": "Email address already exist while creating user",
                }
            return Response(resp, status=status.HTTP_200_OK)
        
        if not username:
            resp = {
                    'errorMessage': "This username is already in use, please try another",
                    'resultCode': '0',
                    'resultDescription': "This email is already in use, please try another"
                }
            return Response(resp, status=status.HTTP_200_OK)
        
        if not password:
            resp = {
                    'errorMessage': "This password is already in use, please try another",
                    'resultCode': '0',
                    'resultDescription': "This email is already in use, please try another"
                }
            return Response(resp, status=status.HTTP_200_OK)
        
        if not first_name:
            resp = {
                    'errorMessage': "This first_name is already in use, please try another",
                    'resultCode': '0',
                    'resultDescription': "This email is already in use, please try another"
                }
            return Response(resp, status=status.HTTP_200_OK)
        
        if not last_name:
            resp = {
                    'errorMessage': "This last_name is already in use, please try another",
                    'resultCode': '0',
                    'resultDescription': "This email is already in use, please try another"
                }
            return Response(resp, status=status.HTTP_200_OK)
        
        
        data= {'email':email,'password':password,'username':username,'first_name':first_name,
               'last_name':last_name,'is_active':is_active,'phone_number':phone_number,
               'alt_contact_number':alt_contact_number,'address':address,'city':city,'state':state,
               'country':country,'zip_code':zip_code,'gender':gender,'nationality':nationality}
        
        context= {'resume':resume,'created_by':created_by,'organization':organization,'image':image}
        user_ser = UserProfileSerializers(data=data,context = context)
        
        if user_ser.is_valid():
            user_ser.save()
            create_user_details(sender=UserProfile, instance=user_ser,created=True, resume=resume,image=image,created_by=created_by,organization=organization)
            resp = {
                "results": "Requested User added successfully",
                "resultDescription": "Requested User added successfully",
                "resultCode": "1"
            }
            return Response(resp, status=status.HTTP_200_OK)
        else:
            org_name = request.data.get('username') 
            ser_key = list(user_ser.errors.keys())[0]
            ser_val = ', '.join(user_ser.errors.get(ser_key))
            raise ResponseError(f"{ser_val}",
                                    f"Attempted to create User {org_name} but raised error {ser_key} {ser_val}")      


    def patch(self,request,pk=None):        
        try:
            user_data = UserProfile.objects.get(pk=pk)
        except:
            raise ResponseError("User id not found",f"Attempt to get user but id not found.")
        else:
            resume =  request.data.get('resume',None)
            image = request.data.get('image',None)
            created_by = self.request.user.email
            email = request.data.get('email',None)
            password = request.data.get('password',None)
            username = request.data.get('username',None)
            first_name = request.data.get('first_name',None)
            last_name = request.data.get('last_name',None)
            is_active = request.data.get('is_active',True)
            phone_number = request.data.get('phone_number',None)
            alt_contact_number = request.data.get('alt_contact_number',None)
            address = request.data.get('address',None)
            city = request.data.get('city',None)
            state = request.data.get('state',None)
            country = request.data.get('country',None)
            zip_code = request.data.get('zip_code',None)
            gender = request.data.get('gender',None)
            nationality = request.data.get('nationality',None)
            organization = request.data.get('organization',None)

            data= {'email':email,'password':password,'username':username,'first_name':first_name,
               'last_name':last_name,'is_active':is_active,'phone_number':phone_number,
               'alt_contact_number':alt_contact_number,'address':address,'city':city,'state':state,
               'country':country,'zip_code':zip_code,'gender':gender,'nationality':nationality}
        
            context= {'resume':resume,'created_by':created_by,'organization':organization,'image':image}

            user_ser = UserProfileSerializers(user_data,data=data,context = context,partial=True)

            if user_ser.is_valid(): 
                print(f"serializers is valid: ",flush=True)
                user_ser.save()                
            else:            
                ser_key = list(user_ser.errors.keys())[0]
                ser_val = ', '.join(user_ser.errors.get(ser_key))          
                raise ResponseError(f"{ser_val}",
                                    f"Attempted to update organizations {user_ser.user_id} but raised error {ser_key} {ser_val}") 


            resp = {
                'results': f"User {username} updated successfully",
                'resultCode': '1',
                'resultDescription': f"Organization {username} updated successfully",
                
            }
            return Response(resp, status=status.HTTP_200_OK) 
    
    
    def delete(self,request,pk=None):
        payload = request.data
        del_reason = payload.get('del_reason')
        valid_reason = fieldvalidator.field_length_validator('del_reason', del_reason)
        if not valid_reason:
            raise ValidationError('Sorry, delete reason lenght must be between 3 to 200 character',
                                      "Attempted deleting user but delete user length was invalid")        
        
        try:
            user_name = UserProfile.objects.get(pk=pk)            
        except Exception as e:
            raise ResponseError("Sorry, User Details not found",
                                f"Attempted to delete user. User doesnot exist") 
        else:    
            user_id = user_name.user_id
            print(f"user_id: {user_id}",flush=True)
            # DeleteUser.objects.create(widget_name=widget_name,
            #                             del_reason=del_reason,
            #                             deleted_by=request.user.email) 
            # X_AxisChartDetails.objects.filter(widget_id = pk).delete()
            # Y_AxisChartDetails.objects.filter(widget_id = pk).delete()            
            user_name.is_active = False
            user_name.save()
        
            resp = {
                'resultDescription': f"User {user_id} is deleted Successfully",
                'resultCode': '1',
                "actionPerformed": f"""User {user_id} has
                                            been deleted successfully.""",
            }
            return Response(resp, status=status.HTTP_200_OK)


class UserProfileListView(ListAPIView):
    queryset = UserProfile.objects.filter(is_active=True).order_by("-id")
    serializer_class = UserProfileSerializers
    # filter_backends = [OrderingFilter, SearchFilter]
    pagination_class = GenericPagination
    # ordering_fields = ["organization_id","organization_name", "organization_type","registered_year","city","state","county","zip_code","cin"]
    # search_fields = ["organization_id","organization_name", "organization_type","registered_year","city","state","county","zip_code","cin"]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        print(f"user: {user}",flush=True)        
        queryset = queryset.exclude(email=user)  
        return queryset
