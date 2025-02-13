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
from utils.jwt_decode import decode_jwt
from .models import Organization, UserProfile, create_user_details
from utils.pagination import GenericPagination
from utils.custom_exception import ResponseError
from utils.custom_exception import ValidationError
from utils.common_validators import FieldValidator
from .CustomJWTSerializers import CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.core.mail import send_mail

fieldvalidator = FieldValidator()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer



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
        role = request.data.get('role',None)

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
        
        context= {'resume':resume,'created_by':created_by,'organization':organization,'image':image,'role':role}
        user_ser = UserProfileSerializers(data=data,context = context)
        
        if user_ser.is_valid():
            user_ser.save()
            create_user_details(sender=UserProfile, instance=user_ser,created=True, resume=resume,image=image,created_by=created_by,organization=organization)
            
            # subject = 'Cadecs send you username and password'
            # message = f"""Username: {username} \n Password: {password}"""
            # from_email = 'your-email@gmail.com'  
            # recipient_list = ['mohd.younus9097@gmail.com']  

            # send_mail(subject, message, from_email, recipient_list)
            
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
            # password = request.data.get('password',None)
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

            data= {'email':email,'username':username,'first_name':first_name,
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
    permission_classes = ([IsAuthenticated])
    queryset = UserProfile.objects.filter(is_active=True).order_by("-id")
    serializer_class = UserProfileSerializers
    # filter_backends = [OrderingFilter, SearchFilter]
    pagination_class = GenericPagination
    # ordering_fields = ["organization_id","organization_name", "organization_type","registered_year","city","state","county","zip_code","cin"]
    # search_fields = ["organization_id","organization_name", "organization_type","registered_year","city","state","county","zip_code","cin"]

    def get_queryset(self):
        queryset = super().get_queryset()
        print(f"self.request: {self.request}",flush=True)
        print(f"self.request: {self.request.headers}",flush=True)
        jwt_token = self.request.headers.get('Authorization')

        jwt_response =  decode_jwt(jwt_token)
        print(f"jwt_response: {jwt_response}",flush=True)
        organization =  jwt_response.get('organization')         

        if organization == 'cadecs':
            user = self.request.user
            print(f"user: {user}",flush=True)        
            queryset = queryset.exclude(email=user)  
            return queryset
        else:
            organization_id = Organization.objects.filter(organization_name=organization,is_deleted=False).first()
            total_user = UserDetails.objects.filter(organization=organization_id).values_list('user',flat=True)
            print(f"total_user: {total_user}",flush=True)

            queryset = queryset.filter(id__in=total_user)  
            return queryset





        
        
        
        


class OrganizationTypeView(APIView):
    permission_classes = ([IsAuthenticated])
    
    def post(self, request):
        name =  request.data.get('name',None)
        description = request.data.get('description',None) 

        if not name:
            resp = {
                    'errorMessage': "Organization type name not found. Kindly input organization type name.",
                    'resultCode': '0',
                    'resultDescription': "Organization type name not found. Kindly input organization type"
                }
            return Response(resp, status=status.HTTP_200_OK)   

        organization_type_lst = OrganizationType.objects.values_list('name', flat=True) 

        print(f"organization_type_lst: {organization_type_lst}",flush=True)
        
        if any(item.lower() == name.lower() for item in organization_type_lst):
            print("Value found!")   
            resp = {
                    'errorMessage': "Organization type already exists. Kindly input another organization type name.",
                    'resultCode': '0',
                    'resultDescription': "Organization type already exists. Kindly input another organization type name."
                }
            return Response(resp, status=status.HTTP_200_OK)     
        
               
        data= {'name':name,'description':description}
        
        org_type_ser = OrganizationTypeSerializer(data=data)
        
        if org_type_ser.is_valid():
            org_type_ser.save()
            resp = {
                "results": "Requested organization type added successfully",
                "resultDescription": "Requested organization type added successfully",
                "resultCode": "1"
            }
            return Response(resp, status=status.HTTP_200_OK)
        else:
            ser_key = list(org_type_ser.errors.keys())[0]
            ser_val = ', '.join(org_type_ser.errors.get(ser_key))
            raise ResponseError(f"{ser_val}",
                                    f"Attempted to create User {name} but raised error {ser_key} {ser_val}")      


    def patch(self,request,pk=None):        
        try:
            org_type = OrganizationType.objects.get(pk=pk)
        except:
            raise ResponseError("Organization type id not found",f"Attempt to get organization type but id not found.")
        else:
            name =  request.data.get('name',None)
            description = request.data.get('description',None)  

            if not name:
                resp = {
                        'errorMessage': "Organization type name not found. Kindly input organization type name.",
                        'resultCode': '0',
                        'resultDescription': "Organization type name not found. Kindly input organization type"
                    }
                return Response(resp, status=status.HTTP_200_OK)

            organization_type_lst = OrganizationType.objects.exclude(name=org_type.name).values_list('name', flat=True) 

            print(f"organization_type_lst: {organization_type_lst}",flush=True)
            
            if any(item.lower() == name.lower() for item in organization_type_lst):
                print("Value found!")   
                resp = {
                        'errorMessage': "Organization type already exists. Kindly input another organization type name.",
                        'resultCode': '0',
                        'resultDescription': "Organization type already exists. Kindly input another organization type name."
                    }
                return Response(resp, status=status.HTTP_200_OK)            
            
            
            data= {'name':name,'description':description}
        
            org_type_ser = OrganizationTypeSerializer(org_type,data=data,partial=True)

            if org_type_ser.is_valid(): 
                org_type_ser.save()                
            else:            
                ser_key = list(org_type_ser.errors.keys())[0]
                ser_val = ', '.join(org_type_ser.errors.get(ser_key))          
                raise ResponseError(f"{ser_val}",
                                    f"Attempted to update organizations {org_type.name} but raised error {ser_key} {ser_val}") 


            resp = {
                'results': f"Organization type {name} updated successfully",
                'resultCode': '1',
                'resultDescription': f"Organization type {name} updated successfully",
                
            }
            return Response(resp, status=status.HTTP_200_OK) 
    
    
    def delete(self,request,pk=None):
        payload = request.data
        del_reason = payload.get('del_reason')
        valid_reason = fieldvalidator.field_length_validator('del_reason', del_reason)
        if not valid_reason:
            raise ValidationError('Sorry, delete reason lenght must be between 3 to 200 character',
                                      "Attempted deleting organization type but delete organization length was invalid")        
        
        try:
            organization_type = OrganizationType.objects.get(pk=pk)            
        except Exception as e:
            raise ResponseError("Sorry, organization type not found",
                                f"Attempted to delete organization type. Organization type doesnot exist") 
        else:    
            organization_type_name = organization_type.name
            organization_type.delete()            
        
            resp = {
                'resultDescription': f"Organization type {organization_type_name} is deleted Successfully",
                'resultCode': '1'
            }
            return Response(resp, status=status.HTTP_200_OK)


class OrganizationTypeListView(ListAPIView):
    queryset = OrganizationType.objects.all().order_by("-id")
    serializer_class = OrganizationTypeSerializer
    filter_backends = [OrderingFilter, SearchFilter]
    pagination_class = GenericPagination
    ordering_fields = ["name"]
    search_fields = ["name"]

class MenuListView(ListAPIView):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    filter_backends = [OrderingFilter, SearchFilter]
    pagination_class = GenericPagination
    ordering_fields = ["name","code"]
    search_fields = ["name","code"]


class RoleAPIView(APIView):
    """CRUD operations for Role"""   

    def post(self, request, *args, **kwargs):
        name =  request.data.get('name',None)
        description = request.data.get('description',None) 

        if not name:            
            resp = {
                    'errorMessage': "Role name not found. Kindly input role name.",
                    'resultCode': '0',
                    'resultDescription': "Role name not found. Kindly input valid role name."
                }
            return Response(resp, status=status.HTTP_200_OK)
        
        role_lst = Role.objects.filter(name=name).values_list('name', flat=True)         
        
        if any(item.lower() == name.lower() for item in role_lst):
            print("Value found!")   
            resp = {
                    'errorMessage': "Role name already exists. Kindly input another role name.",
                    'resultCode': '0',
                    'resultDescription': "Role name already exists. Kindly input role name."
                }
            return Response(resp, status=status.HTTP_200_OK) 

        
        data= {'name':name,'description':description}
        role_ser = RoleSerializer(data=data)
        if role_ser.is_valid():
            role_ser.save()
            resp = {
                "results": f"Requested Role {name} added successfully",
                "resultDescription": f"Requested Role {name} added successfully",
                "resultCode": "1"
            }
            return Response(resp, status=status.HTTP_200_OK)
        else:
            ser_key = list(role_ser.errors.keys())[0]
            ser_val = ', '.join(role_ser.errors.get(ser_key))
            raise ResponseError(f"{ser_val}",
                                    f"Attempted to create User {name} but raised error {ser_key} {ser_val}")      


    def patch(self, request, pk, *args, **kwargs):        
        role = Role.objects.filter(id=pk).first()
        if not role:
            raise ResponseError("Role id not found",f"Attempt to create role but id not found.")
        
        name =  request.data.get('name',None)
        description = request.data.get('description',None) 

        if not name:            
            resp = {
                    'errorMessage': "Role name not found. Kindly input role name.",
                    'resultCode': '0',
                    'resultDescription': "Role name not found. Kindly input valid role name."
                }
            return Response(resp, status=status.HTTP_200_OK)
        

        role_lst = Role.objects.exclude(name=role.name).values_list('name', flat=True)         
        
        if any(item.lower() == name.lower() for item in role_lst):
            print("Value found!")   
            resp = {
                    'errorMessage': "Role name already exists. Kindly input another role name.",
                    'resultCode': '0',
                    'resultDescription': "Role name already exists. Kindly input role name."
                }
            return Response(resp, status=status.HTTP_200_OK)            
        
        data= {'name':name,'description':description}
        role_ser = RoleSerializer(role, data=data,partial=True)
        if role_ser.is_valid():
            role_ser.save()
            resp = {
                "results": f"Requested Role {name} updated successfully",
                "resultDescription": f"Requested Role {name} updated successfully",
                "resultCode": "1"
            }
            return Response(resp, status=status.HTTP_200_OK)
        else:
            ser_key = list(role_ser.errors.keys())[0]
            ser_val = ', '.join(role_ser.errors.get(ser_key))
            raise ResponseError(f"{ser_val}",
                                    f"Attempted to create User {name} but raised error {ser_key} {ser_val}")      

    def delete(self, request, pk, *args, **kwargs):
        """Delete a role."""   
    
        payload = request.data
        del_reason = payload.get('del_reason')
        valid_reason = fieldvalidator.field_length_validator('del_reason', del_reason)
        if not valid_reason:
            raise ValidationError('Sorry, delete reason lenght must be between 3 to 200 character',
                                      "Attempted deleting role but delete role length was invalid")        
        
        try:
            role = Role.objects.get(pk=pk)            
        except Exception as e:
            raise ResponseError("Sorry, role name not found",
                                f"Attempted to delete role. Role type doesnot exist") 
        else:    
            role_name = role.name
            role.delete()            
        
            resp = {
                'resultDescription': f"Role name:{role_name} is deleted Successfully",
                'resultCode': '1'
            }
            return Response(resp, status=status.HTTP_200_OK)

class RoleListView(ListAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    filter_backends = [OrderingFilter, SearchFilter]
    pagination_class = GenericPagination
    ordering_fields = ["name"]
    search_fields = ["name"]


























class MediaFileListView(APIView):
    """
    APIView to list all media files and their S3 URLs.
    """
    def get(self, request, *args, **kwargs):
        media_files = MediaFile.objects.all()
        serializer = MediaFileSerializer(media_files, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        serializer = MediaFileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # This saves the file to your S3 bucket
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   