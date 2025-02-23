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
from .models import Organization, UserProfile #, create_user_details
from utils.pagination import GenericPagination
from utils.custom_exception import ResponseError
from utils.custom_exception import ValidationError
from utils.common_validators import FieldValidator
from .CustomJWTSerializers import CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.core.mail import send_mail
from .utils.extract_resume import ExtractData

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
        organization_name = request.data.get('organization_name')
        email = request.data.get('email')         
        user = self.request.user          
        context={'created_by':user}
        orgs_ser = OrganizationSerializer(data=request.data,context=context)       
        
        if orgs_ser.is_valid():
            orgs_ser.save()

            try:
                subject = 'Welcome letter to Cadecs'
                message = f"""Hi {organization_name},\n\nYours organization registered successfully in cades.\n\nThanks & Regrads\nCADECS"""
                from_email = 'cadecsdevelopment@gmail.com'  
                recipient_list = [email]  

                send_mail(subject, message, from_email, recipient_list)
            except:
                pass
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

            # organization_logo = request.data.get('organization_logo',None)
            # print(f"organization_logo: {organization_logo}",flush=True)
            organization_name = request.data.get('organization_name')  
            organization_type = request.data.get('organization_type')
            organization_logo = request.data.get('organization_logo',None)
            ceo_name = request.data.get('ceo_name')
            registered_year = request.data.get('registered_year')
            tax_number = request.data.get('tax_number')  
            contact_person = request.data.get('contact_person') 
            email = request.data.get('email')
            website_url = request.data.get('website_url') 
            phone_number = request.data.get('phone_number') 
            alt_contact_number = request.data.get('alt_contact_number') 
            address = request.data.get('address')
            city = request.data.get('city') 
            state = request.data.get('state') 
            county = request.data.get('county') 
            zip_code = request.data.get('zip_code')      
            cin = request.data.get('cin')
            created_by = self.request.user

            print(f"organization_logo: {organization_logo}",flush=True)

            

            if organization_logo is None or organization_logo=='':
                data = {'organization_logo': None,'organization_name':organization_name,
                    'organization_type':organization_type,'ceo_name':ceo_name,
                    'registered_year':registered_year,'tax_number':tax_number,'contact_person':contact_person,
                    'email':email,'website_url':website_url,'phone_number':phone_number,'alt_contact_number':alt_contact_number,
                    'address':address,'city':city,'state':state,'county':county,'zip_code':zip_code,'cin':cin,'created_by':created_by}
            else:
                if not str(organization_logo).startswith("https://"):
                    data = {'organization_logo': organization_logo,'organization_name':organization_name,
                    'organization_type':organization_type,'ceo_name':ceo_name,
                    'registered_year':registered_year,'tax_number':tax_number,'contact_person':contact_person,
                    'email':email,'website_url':website_url,'phone_number':phone_number,'alt_contact_number':alt_contact_number,
                    'address':address,'city':city,'state':state,'county':county,'zip_code':zip_code,'cin':cin,'created_by':created_by}
                else:                
                    data = {'organization_name':organization_name,
                    'organization_type':organization_type,'ceo_name':ceo_name,
                    'registered_year':registered_year,'tax_number':tax_number,'contact_person':contact_person,
                    'email':email,'website_url':website_url,'phone_number':phone_number,'alt_contact_number':alt_contact_number,
                    'address':address,'city':city,'state':state,'county':county,'zip_code':zip_code,'cin':cin,'created_by':created_by}

            orgs_ser = OrganizationSerializer(org_data,data=data,partial=True)

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
            # organization_id.is_deleted = True
            organization.delete()
        
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
            # create_user_details(sender=UserProfile, instance=user_ser,created=True, resume=resume,image=image,created_by=created_by,organization=organization)
            
            try:
                subject = 'Cadecs send you username and password'
                message = f"""Welcome {username}, your username password given below: \n Username: {username} \n Password: {password}"""
                from_email = 'cadecsdevelopment@gmail.com'  
                recipient_list = [email]  

                send_mail(subject, message, from_email, recipient_list)
            except:
                pass
            
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
            user_id = user_name.username
            print(f"user_id: {user_id}",flush=True)

            user_detail = UserDetails.objects.filter(user_id=user_name.id).delete()  
                        
            # user_name.is_active = False
            # user_name.save()

            user_name.delete()
        
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



class ExtractResumeDetailsView(APIView):
    def post(self,request):        
        resume =  request.data.get('resume',None)        
        if str(resume).lower().endswith(".pdf"):
            extract_obj = ExtractData()
            extract_data = extract_obj.extract_information(resume)

            email = extract_data.get('email')
            phone = extract_data.get('phone')

            if not email and not phone:
                resp = {
                'result': "Invalid file. kindly insert resume.",
                'resultCode': '0',
                "resultDescription": f"""Invalid file. kindly pass valid pdf file.""",
                }
                return Response(resp, status=status.HTTP_200_OK)            
            
            resp = {
                'result': extract_data,
                'resultCode': '1',
                "resultDescription": f"""Extract data from resume.""",
            }
            return Response(resp, status=status.HTTP_200_OK)
        
        else:
            resp = {
                'result': [],
                'resultCode': '0',
                "resultDescription": f"""Invalid file. kindly pass valid pdf file.""",
            }
            return Response(resp, status=status.HTTP_200_OK)
        

class ExtractOrganizationDetailsView(APIView):
    def post(self,request):
        
        org_file =  request.data.get('org_file',None)        
        if str(org_file).lower().endswith(".pdf"):
            extract_obj = ExtractData()
            extract_data = extract_obj.extract_text_from_pdf(org_file)

            lines = extract_data.split("\n")

            org_details = {}
            org_name = None
            org_email = None
            for line in lines:
                print(f"line: {line}")
                data_lst=line.split(':')
                print(data_lst)

                if 'Organiza' in line:
                    org_details['org_name'] = data_lst[2].lstrip()
                    org_name = data_lst[2].lstrip()
                if 'Org Email' in line:
                    org_details['org_email'] = data_lst[1].lstrip()
                    org_email = data_lst[1].lstrip()
                if 'Org contact' in line and not 'Org contact name' in line:
                    org_details['org_contact'] = data_lst[1].lstrip()
                if 'Org contact name' in line:
                    org_details['org_contact_name'] = data_lst[1].lstrip()
                if 'Website Url'  in line:
                    org_details['website_url'] = data_lst[3][2:]            

            if not org_name and not org_email:
                resp = {
                'result': "Invalid file. kindly insert valid organization details file.",
                'resultCode': '0',
                "resultDescription": f"""Invalid file. kindly pass valid pdf file.""",
                }
                return Response(resp, status=status.HTTP_200_OK)            
            
            resp = {
                'result': org_details,
                'resultCode': '1',
                "resultDescription": f"""Extract data from organization details file.""",
            }
            return Response(resp, status=status.HTTP_200_OK)
        
        else:
            resp = {
                'result': [],
                'resultCode': '0',
                "resultDescription": f"""Invalid file. kindly pass valid pdf file.""",
            }
            return Response(resp, status=status.HTTP_200_OK)

class ExtractfacilitylocationView(APIView):
    def post(self,request):
        
        facility_location_file =  request.data.get('file',None)        
        if str(facility_location_file).lower().endswith(".pdf"):
            extract_obj = ExtractData()
            extract_data = extract_obj.extract_text_from_pdf(facility_location_file)

            lines = extract_data.split("\n")

            facility_location_lst = []
            valid_file = False            
            
            for line in lines:
                if 'Zip Code Client' in line:
                    valid_file = True
                    
                zip_code_dict = {}
                if 'Zip Code Client' not in line:
                    print(f"line: {line}")
                    data = line.split()
                    print(f"data: {data}")
                    try:

                        zip_code_dict['zip_code'] = data[0]
                        zip_code_dict['client_ratio'] = data[1]
                    except:
                        pass
                    facility_location_lst.append(zip_code_dict)           

            if not valid_file:
                resp = {
                'result': "Invalid file. kindly insert valid client location file.",
                'resultCode': '0',
                "resultDescription": f"""Invalid file. kindly pass valid pdf file.""",
                }
                return Response(resp, status=status.HTTP_200_OK)            
            
            resp = {
                'result': facility_location_lst,
                'resultCode': '1',
                "resultDescription": f"""Extract data from client location file.""",
            }
            return Response(resp, status=status.HTTP_200_OK)
        
        else:
            resp = {
                'result': [],
                'resultCode': '0',
                "resultDescription": f"""Invalid file. kindly pass valid pdf file.""",
            }
            return Response(resp, status=status.HTTP_200_OK)













class MediaFileListView(APIView):
    """
    APIView to list all media files and their S3 URLs.
    """
    def get(self, request, *args, **kwargs):
        subject = 'Cadecs send you username and password'
        message = f"""Hi Younus How are you"""
        from_email = 'cadecsdevelopment@gmail.com'  
        recipient_list = ['younus.mohd9097@gmail.com']  

        send_mail(subject, message, from_email, recipient_list)

        print("mail send successfully",flush=True)
        media_files = MediaFile.objects.all()
        serializer = MediaFileSerializer(media_files, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):

        
        serializer = MediaFileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # This saves the file to your S3 bucket
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   