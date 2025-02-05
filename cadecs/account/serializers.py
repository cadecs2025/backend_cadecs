from rest_framework import serializers
from .models import * # Organization, UserProfile,ProfileImage,UserDetails
from utils.custom_exception import ValidationError


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
    
    
    

    # def validate(self, data):       
        
    #     organization_name = data.get('organization_name') 
    #     if not organization_name:
    #         raise ValidationError("organization_name not found. Please input valid organization_name.")

    #     organization_type = data.get('organization_type')
    #     if not organization_type:
    #         raise ValidationError("organization_type not found. Please input valid organization_type")
        
    #     organization_logo = data.get('organization_logo')
    #     if not organization_logo:
    #         raise ValidationError("organization_logo not found. Please input valid organization_logo")
        
    #     ceo_name = data.get('ceo_name')
    #     if not ceo_name:
    #         raise ValidationError("ceo_name not found. Please input valid ceo_name.")
        
    #     registered_year = data.get('registered_year')  
    #     if not registered_year:
    #         raise ValidationError("registered_year not found. Please input valid registered_year")
        
    #     tax_number = data.get('tax_number') 
    #     if not tax_number:
    #         raise ValidationError("tax_number not found. Please input valid tax_number")
        
    #     contact_person = data.get('contact_person') 
    #     if not contact_person:
    #         raise ValidationError("contact_person not found. Please input valid contact_person")
        
    #     email = data.get('email')
    #     if not email:
    #         raise ValidationError("email not found. Please input valid email")       
        
    #     website_url = data.get('website_url')
    #     phone_number = data.get('phone_number')
    #     alt_contact_number = data.get('alt_contact_number')
    #     address = data.get('address')
    #     city = data.get('city')
    #     state = data.get('state')
    #     county = data.get('county')
    #     zip_code = data.get('zip_code')
    #     cin = data.get('cin')       
    #     return data
    

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


        print(f"""{organization_name}-{organization_type}-{ceo_name}-{registered_year}-{tax_number}-{contact_person}-{email}-{website_url}-{phone_number}-{alt_contact_number}-{address}-{city}-{state}-{county}-{zip_code}-{cin}-{created_by}""")
        
        org_obj = Organization.objects.create(
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

        print(f"""{instance.organization_name}-{instance.organization_type}-{instance.website_url}-{instance.email}-{instance.phone_number}""")     
        
        instance.save()
        return instance

class UserDetailsSerializers(serializers.ModelSerializer): 
    organization_id = serializers.SerializerMethodField()   
    class Meta:
        model = UserDetails
        fields = '__all__'
    
    def get_organization_id(self,obj): 
        print(f"bcdnjcbd vjdhjv dhvjdv jd{obj.organization.id}",flush=True)       
        organization_id = Organization.objects.filter(id=obj.organization.id).values('organization_id').first()
        print(f"organization_id: {organization_id}",flush=True)
        organiz = None
        if organization_id:
            organiz = organization_id.get('organization_id')
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

    # def get_image(self,obj):        
    #     image_details = ProfileImage.objects.filter(user=obj.id).order_by('-id').values('image').first()
    #     if image_details:
    #         print(f"image_details: {image_details}",flush=True)
    #         image  = image_details.get('image')
    #         if image:
    #             return image
    #     return 'media/profileImage/default.png'
    

    def get_image(self, obj):
        request = self.context.get('request')
        DefaultImage = '/media/profileImage/default.png'
        default_img = request.build_absolute_uri(DefaultImage)
        user_profile = ProfileImage.objects.filter(user=obj.id).first()

        print(f"user_profile: {user_profile}",flush=True)
        if user_profile:
            image_url = user_profile.image.url
            print(f"image_url: {image_url}")
            if image_url:
                # return image_url
                return request.build_absolute_uri(image_url)
        return default_img
    
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
        created_by = self.context.get("created_by",None)

        print(f"Organizations:{organization_id} resume: {resume} created : {created_by}",flush=True)
        try:
            organization_id = int(organization_id)
            org_obj = Organization.objects.get(id=organization_id)
            print(f"Organizations objects: {org_obj}",flush=True)
        except Exception as ex:
            print(f"ex: {ex}",flush=True)
        else:           
            UserDetails.objects.create(user = user,
                                    organization=org_obj,
                                    resume=resume,
                                    created_by = created_by,
                                    )
            print("UserDetails details created successfully",flush=True)

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

        print(f"created_by: {created_by}",flush=True)

        ProfileImage.objects.filter(user=instance).update(image=image)

        try:
            organization_id = int(organization_id)
            org_obj = Organization.objects.get(id=organization_id)
            print(f"Organizations objects: {org_obj}",flush=True)
        except Exception as ex:
            print(f"ex: {ex}",flush=True)
        else:           
            user_details=UserDetails.objects.filter(user = instance.id)
            print(f"user_details: {user_details}",flush=True)           

            if user_details:
                user_details.update(            
                                    organization=org_obj,
                                    resume=resume,
                                    updated_by = created_by,
                                    )
            else:
                UserDetails.objects.create(user = instance,
                                    organization=org_obj,
                                    resume=resume,
                                    created_by = created_by,
                                    )                           
        
        instance.save()
        return instance

        
class OrganizationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationType
        fields = ['id','name','description']
    
    def create(self, validated_data):         
        name = validated_data.pop('name')     
        description = validated_data.pop('description')           

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