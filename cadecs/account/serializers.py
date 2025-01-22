from rest_framework import serializers
from .models import Organization
from utils.custom_exception import ValidationError

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'
        read_only_fields = ['organization_id','created_at','created_by']
    

    def validate(self, data):       
        
        organization_name = data.get('organization_name') 
        if not organization_name:
            raise ValidationError("organization_name not found. Please input valid organization_name.")

        organization_type = data.get('organization_type')
        if not organization_type:
            raise ValidationError("organization_type not found. Please input valid organization_type")
        
        organization_logo = data.get('organization_logo')
        if not organization_logo:
            raise ValidationError("organization_logo not found. Please input valid organization_logo")
        
        ceo_name = data.get('ceo_name')
        if not ceo_name:
            raise ValidationError("ceo_name not found. Please input valid ceo_name.")
        
        registered_year = data.get('registered_year')  
        if not registered_year:
            raise ValidationError("registered_year not found. Please input valid registered_year")
        
        tax_number = data.get('tax_number') 
        if not tax_number:
            raise ValidationError("tax_number not found. Please input valid tax_number")
        
        contact_person = data.get('contact_person') 
        if not contact_person:
            raise ValidationError("contact_person not found. Please input valid contact_person")
        
        email = data.get('email')
        if not email:
            raise ValidationError("email not found. Please input valid email")       
        
        website_url = data.get('website_url')
        phone_number = data.get('phone_number')
        alt_contact_number = data.get('alt_contact_number')
        address = data.get('address')
        city = data.get('city')
        state = data.get('state')
        county = data.get('county')
        zip_code = data.get('zip_code')
        cin = data.get('cin')       
        return data
    

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


        print(f"""{organization_name}-{organization_type}-{organization_logo}-{ceo_name}-{registered_year}-{tax_number}-{contact_person}-{email}-{website_url}-{phone_number}-{alt_contact_number}-{address}-{city}-{state}-{county}-{zip_code}-{cin}-{created_by}""")
        
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

   