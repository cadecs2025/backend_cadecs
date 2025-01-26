from django.db import models
from django.contrib.auth.models import User

class BaseModel(models.Model):
    created_by = models.ForeignKey(User,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(null=True)
    updated_at = models.DateTimeField(null=True)
    is_deleted = models.BooleanField(default=False)
    status = models.BooleanField(default=True)


class Organization(BaseModel):
    organization_id = models.IntegerField(unique=True, editable=False)
    organization_name = models.CharField(max_length=250)
    organization_type = models.CharField(max_length=100)
    organization_logo = models.FileField(upload_to='images/',null=True)
    ceo_name = models.CharField(max_length=100,null=True)
    registered_year = models.CharField(max_length=50)
    tax_number = models.CharField(max_length=100,null=True)
    contact_person = models.CharField(max_length=100)
    email = models.CharField(max_length=100,null=True)
    website_url = models.CharField(max_length=100,null=True) 
    phone_number = models.CharField(max_length=100)
    alt_contact_number = models.CharField(max_length=100)   
    address = models.CharField(max_length=350)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    county = models.CharField(max_length=100)    
    zip_code = models.CharField(max_length=100)
    cin = models.CharField(max_length=100,null=True)

    def save(self, *args, **kwargs):
        if not self.organization_id:
            # Get the last organization ID
            last_organization = Organization.objects.order_by('-id').first()
            if last_organization:
                new_id = last_organization.organization_id + 1
            else:
                # First employee
                new_id = 10001
            self.organization_id = f"{new_id}"
        super().save(*args, **kwargs)  

    def __str__(self):
        return self.organization_name
    
       
    
     
    
    
    

