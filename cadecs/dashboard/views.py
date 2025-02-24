from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from account.models import Organization, UserProfile,UserDetails,ClientLocation
from utils.jwt_decode import decode_jwt



class DashboardView(APIView):
    permission_classes = [IsAuthenticated] 

    def get(self,request):    
        jwt_token= request.META.get('HTTP_AUTHORIZATION')                                
        jwt_response =  decode_jwt(jwt_token)            
        organization =  jwt_response.get('organization')
        role =  jwt_response.get('role') 
        user_id = jwt_response.get('user_id')                    

        if organization == 'cadecs': 
            if role == 'Super Admin':
                total_user = UserProfile.objects.filter(is_active=True)
                total_user = total_user.exclude(id=user_id)  
                user_count=total_user.count()
                
                total_org = Organization.objects.filter(is_deleted=False).count()  

                client_location = ClientLocation.objects.values('zip').distinct()
                # client_location = total_user.exclude(id=user_id)                      
                client_location_count=client_location.count()        
                
                dict_data = {'total_user':user_count,'total_org': total_org,'total_client_location': client_location_count}
            else:
                dict_data = {}
        else:
            if role == 'Admin':
                organization_id = Organization.objects.filter(organization_name=organization,is_deleted=False).first()
                print(f"organization_id: {organization_id}",flush=True)
                total_user = UserDetails.objects.filter(organization=organization_id)
                total_user = total_user.exclude(id=user_id)                      
                user_count=total_user.count()

                client_location = ClientLocation.objects.filter(organization=organization_id).values('zip').distinct()
                # client_location = total_user.exclude(id=user_id)                      
                client_location_count=client_location.count()
                dict_data = {'total_user':user_count, 'total_client_location': client_location_count}
            else:
                dict_data = {}                
        
        resp = {
            'results': dict_data,            
            'resultCode': '1',
            'resultDescription': f'Get dashboard details.'
        }
        return Response(resp, status=status.HTTP_200_OK)
