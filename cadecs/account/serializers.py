from rest_framework import serializers
from .models import * # Organization, UserProfile,ProfileImage,UserDetails
from utils.custom_exception import ValidationError
import os
from .models import MediaFile
from utils.upload_file import FileUpload
from cadecs.settings import MEDIA_URL


class MediaFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaFile
        fields = ['id', 'file']
    
    def create(self, validated_data):
        file = validated_data.get('file') 
        obj, media_obj = MediaFile.objects.get_or_create(file=file)

        print(f"obj fle name file: {obj.file}",flush=True)  

        file_obj = FileUpload()
        file_obj.s3_file_upload(file_path= obj.file)  
        
        print("uploaded successfully",flush=True)      
        return obj


class OrganizationDropDownSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id','organization_name']
        # read_only_fields = ['organization_id','created_at','created_by']

class OrganizationSerializer(serializers.ModelSerializer):
    # organization_logo = serializers.SerializerMethodField()
    class Meta:
        model = Organization
        fields = '__all__'
        read_only_fields = ['organization_id','created_at','created_by']    

    def create(self, validated_data):
        organization_name = validated_data.get('organization_name')  
        organization_type = validated_data.get('organization_type')
        organization_logo = validated_data.get('organization_logo')
        ceo_name = validated_data.get('ceo_name')
        registered_year = validated_data.get('registered_year')
        tax_number = validated_data.get('tax_number')  
        contact_person = validated_data.get('contact_person') 
        email = validated_data.get('email')
        website_url = validated_data.get('website_url') 
        phone_number = validated_data.get('phone_number') 
        alt_contact_number = validated_data.get('alt_contact_number') 
        address = validated_data.get('address')
        city = validated_data.get('city') 
        state = validated_data.get('state') 
        county = validated_data.get('county') 
        zip_code = validated_data.get('zip_code')      
        cin = validated_data.get('cin')
        created_by = self.context.get("created_by")
        
        org_obj,created = Organization.objects.get_or_create(
                                            organization_name=organization_name, 
                                            organization_type=organization_type,
                                            organization_logo=organization_logo, 
                                            ceo_name=ceo_name, 
                                            registered_year=registered_year,
                                            tax_number=tax_number,
                                            contact_person=contact_person,
                                            email = email,
                                            website_url=website_url,
                                            phone_number =phone_number,
                                            alt_contact_number=alt_contact_number,
                                            address=address,
                                            city = city,
                                            state = state,
                                            county = county, 
                                            zip_code = zip_code,
                                            cin = cin,
                                            created_by = created_by          
                                            )  

        print(f"obj fle name file: {org_obj.organization_logo}",flush=True)  

        file_obj = FileUpload()
        file_obj.s3_file_upload(file_path= org_obj.organization_logo)  
        
        print("uploaded successfully",flush=True)  
        # os.remove(str(org_obj.organization_logo))   
        print("file removed successfully",flush=True)        
        
        return org_obj
    

    def update(self, instance, validated_data):            
        
        instance.organization_name = validated_data.get('organization_name',instance.organization_name)
        instance.organization_type = validated_data.get('organization_type',instance.organization_type)        
        instance.organization_logo = validated_data.get('organization_logo',instance.organization_logo)
        instance.ceo_name = validated_data.get('ceo_name',instance.ceo_name)
        instance.registered_year = validated_data.get('registered_year',instance.registered_year)
        instance.tax_number = validated_data.get('tax_number',instance.tax_number)
        instance.contact_person = validated_data.get('contact_person',instance.contact_person)
        instance.email = validated_data.get('email',instance.email)
        instance.website_url = validated_data.get('website_url',instance.website_url)   
        instance.phone_number = validated_data.get('phone_number',instance.phone_number)
        instance.alt_contact_number = validated_data.get('alt_contact_number',instance.alt_contact_number)  
        instance.address = validated_data.get('address',instance.address) 
        instance.city = validated_data.get('city',instance.city) 
        instance.state = validated_data.get('state',instance.state) 
        instance.county = validated_data.get('county',instance.county) 
        instance.zip_code = validated_data.get('zip_code',instance.zip_code) 
        instance.cin = validated_data.get('cin',instance.cin)
        instance.created_by = validated_data.get('created_by',instance.created_by)

        instance.save()

        print(f"obj fle name file: {instance.organization_logo}",flush=True)  
        print(f"obj fle name file: {str(instance.organization_logo)}",flush=True)

        # if not str(instance.organization_logo).startswith("https://"):
        file_obj = FileUpload()
        file_obj.s3_file_upload(file_path= str(instance.organization_logo))  
        
        print("uploaded successfully",flush=True)    
            # os.remove(str(instance.organization_logo))
        # else:
        #     validated_data.pop(instance.organization_logo)

        return instance

class UserDetailsSerializers(serializers.ModelSerializer): 
    organization_id = serializers.SerializerMethodField()  
    organization =  serializers.SerializerMethodField()
    role =  serializers.SerializerMethodField()
    role_id =  serializers.SerializerMethodField()
    class Meta:
        model = UserDetails
        fields = '__all__'
    
    def get_organization_id(self,obj): 
        organization_id = Organization.objects.filter(id=obj.organization.id).values('id').first()
        organiz = None
        if organization_id:
            organiz = organization_id.get('id')
        return organiz
    
    def get_organization(self,obj): 
        organization_name = Organization.objects.filter(id=obj.organization.id).values('organization_name').first()
        organiz = None
        if organization_name:
            organiz = organization_name.get('organization_name')
        return organiz
    
    def get_role(self,obj): 
        role = Role.objects.filter(id=obj.role.id).values('name').first()
        organiz = None
        if role:
            organiz = role.get('name')
        return organiz
    
    def get_role_id(self,obj): 
        role = Role.objects.filter(id=obj.role.id).values('id').first()
        organiz = None
        if role:
            organiz = role.get('id')
        return organiz


class UserProfileSerializers(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    user_detail = serializers.SerializerMethodField()
    class Meta:
        model = UserProfile
        fields = [
            'id',
            'user_id',
            'email',
            'password',
            'username',
            'first_name',
            'last_name',            
            'is_active',
            'phone_number',            
            'alt_contact_number',
            'address',
            'city',
            'state',
            'country',
            'zip_code',
            'gender',
            'nationality',
            'image',
            'user_detail'

        ]
        read_only_fields = ['user_id','image','user_detail']
    

    def get_image(self, obj):
        # request = self.context.get('request')
        DefaultImage = f'{MEDIA_URL}media/default.png'
        # default_img = request.build_absolute_uri(DefaultImage)
        user_profile = ProfileImage.objects.filter(user=obj.id).first()

        print(f"user_profile: {user_profile}",flush=True)
        if user_profile:
            image_url = user_profile.image
            print(f"image_url: {image_url}",flush=True)
            if image_url:
                # return image_url
                return f'{MEDIA_URL}{image_url}' #request.build_absolute_uri(image_url)
        return DefaultImage
    
    def get_user_detail(self,obj):        
        user_detail_details = UserDetailsSerializers(UserDetails.objects.filter(user=obj.id), many=True)
        return user_detail_details.data
    
    
    def create(self, validated_data):         
        password = validated_data.pop('password')
        user = UserProfile.objects.create(**validated_data)   
        user.set_password(password)
        user.save()
               

        organization_id = self.context.get("organization")
        resume = self.context.get("resume",None)
        image = self.context.get("image",None)
        created_by = self.context.get("created_by",None)
        role_id = self.context.get("role",None)

        role_obj = None
        try:
            role_obj = Role.objects.get(id=role_id)
        except:
            pass

        try:
            image_obj,created = ProfileImage.objects.get_or_create(user = user,
                                            image=image                                            
                                            )
            print("profile image created successfully",flush=True)
            file_obj = FileUpload()
            file_obj.s3_file_upload(file_path= image_obj.image) 

            # if image:
            #     print("uploaded successfully",flush=True) 
            #     os.remove(str(image_obj.image))           
            
        except:
            pass  

        try:
            organization_id = int(organization_id)
            org_obj = Organization.objects.get(id=organization_id)
            print(f"Organizations objects: {org_obj}",flush=True)
        except Exception as ex:
            print(f"ex: {ex}",flush=True)
        else:           
            user_detail_obj,created = UserDetails.objects.get_or_create(user = user,
                                    organization=org_obj,
                                    resume=resume,
                                    created_by = created_by,
                                    role= role_obj
                                    )
            
            print("UserDetails details created successfully",flush=True)

            file_obj = FileUpload()
            file_obj.s3_file_upload(file_path= user_detail_obj.resume)  
            
            print("uploaded successfully",flush=True)  
            # if resume:
            #     os.remove(str(user_detail_obj.resume)) 

        return user 
        
    def update(self, instance, validated_data):            
        
        instance.email = validated_data.get('email',instance.email)
        instance.is_active = validated_data.get('is_active',instance.is_active)        
        instance.phone_number = validated_data.get('phone_number',instance.phone_number)
        instance.alt_contact_number = validated_data.get('alt_contact_number',instance.alt_contact_number)
        instance.address = validated_data.get('address',instance.address)
        instance.city = validated_data.get('city',instance.city)
        instance.state = validated_data.get('state',instance.state)
        instance.country = validated_data.get('country',instance.country)
        instance.zip_code = validated_data.get('zip_code',instance.zip_code)   
        instance.gender = validated_data.get('gender',instance.gender)
        instance.nationality = validated_data.get('nationality',instance.nationality) 

        organization_id = self.context.get("organization")
        resume = self.context.get("resume",None)
        created_by = self.context.get("created_by",None)
        image = self.context.get("image",None)
        role_id = self.context.get("role",None)
        
        role_obj = None
        if role_id:            
            try:
                role_obj = Role.objects.get(id=role_id)
            except:
                pass
        else:
            users= UserDetails.objects.filter(user = instance.id).first()
            role_obj = users.role

            # if not resume:
                # resume = str(users.resume)
                # print(f"resume: {resume}",flush=True)


        print(f"created_by: {created_by}",flush=True)
        file_obj = FileUpload()
        # if image:            
        ProfileImage.objects.filter(user=instance).delete()            
        try:
            image_obj,created = ProfileImage.objects.get_or_create(user = instance,
                                            image=image                                            
                                            )
            print("profile image created successfully",flush=True)
            
            file_obj.s3_file_upload(file_path= image_obj.image) 

            # if image:
            #     print("uploaded successfully",flush=True) 
            #     os.remove(str(image_obj.image)) 
        except:
            pass  

        
        try:
            organization_id = int(organization_id)
            org_obj = Organization.objects.get(id=organization_id)
            print(f"Organizations objects: {org_obj}",flush=True)
        except Exception as ex:
            print(f"ex: {ex}",flush=True)
        else:                      
            UserDetails.objects.filter(user = instance.id).delete()            
            user_detail_obj,created = UserDetails.objects.get_or_create(user = instance,
                                organization=org_obj,
                                resume=resume,
                                created_by = created_by,
                                role= role_obj
                                )
            
            print("UserDetails details created successfully",flush=True)

            file_obj = FileUpload()
            file_obj.s3_file_upload(file_path= user_detail_obj.resume)  
            
            print("uploaded successfully",flush=True)  
            #if resume:
            #    os.remove(str(user_detail_obj.resume))                                  
        
        instance.save()
        return instance

        
class OrganizationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationType
        fields = ['id','name','description']
    
    def create(self, validated_data):         
        name = validated_data.get('name')     
        description = validated_data.get('description')           

        org_type_obj = OrganizationType.objects.create(
                                            name=name, 
                                            description=description                                                     
                                            )           
        return org_type_obj
    
    def update(self, instance, validated_data):            
        
        instance.name = validated_data.get('name',instance.name)
        instance.description = validated_data.get('description',instance.description) 

        instance.save()
        return instance  

class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ['id', 'name', 'code', 'description']

class RolePermissionSerializer(serializers.ModelSerializer):
    menu = MenuSerializer()  # Nested menu serializer

    class Meta:
        model = RolePermission
        fields = ['id', 'menu', 'can_view', 'can_edit', 'can_delete']

class RoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Role
        fields = ['id','name', 'description']
    
    def create(self, validated_data):         
        name = validated_data.get('name')     
        description = validated_data.get('description')           

        role_obj = Role.objects.create( name=name, 
                                        description=description                                                     
                                        )           
        return role_obj
    
    def update(self, instance, validated_data):            
        
        instance.name = validated_data.get('name',instance.name)
        instance.description = validated_data.get('description',instance.description) 

        instance.save()
        return instance 


