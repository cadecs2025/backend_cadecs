from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser, Permission
from django.utils import timezone
from os.path import splitext
from django.db.models.signals import post_save
from django.dispatch import receiver
import os
import mimetypes
import boto3
from utils.upload_file import FileUpload





class UserProfile(AbstractUser):    
    user_id = models.CharField(max_length=30,unique=True, editable=False)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    phone_number = models.CharField(max_length=20, null=True,blank=True)    
    alt_contact_number = models.CharField(max_length=100,null=True)    
    address = models.CharField(max_length=150,null=True,blank=True)
    city = models.CharField(max_length=20, null=True, blank=True)    
    state = models.CharField(max_length=20, null=True, blank=True)    
    country = models.CharField(max_length=20, null=True, blank=True)   
    zip_code = models.CharField(max_length=20, null=True, blank=True) 
    gender = models.CharField(max_length=20, null=True, blank=True) 
    nationality = models.CharField(max_length=20, null=True, blank=True)       
    password_changed_at = models.DateTimeField(auto_now=True)
    user_invalid_attempt = models.IntegerField(default=0)
    user_invalid_attempt_at = models.DateTimeField(null=True, blank=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        if not self.user_id:
            # Get the last organization ID
            last_user = UserProfile.objects.order_by('-id').first()
            if last_user:
                numeric_value = last_user.user_id[2:]
                new_numeric_value = int(numeric_value) + 1
                new_user_id = f"CD{new_numeric_value}"
            else:
                # First employee
                new_numeric_value = 10001
                new_user_id = f"CD{new_numeric_value}"
            self.user_id = f"{new_user_id}"
        super().save(*args, **kwargs) 
    
DefaultImage = 'media/default.png'
class ProfileImage(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='media/', default=DefaultImage)

class BaseModel(models.Model):
    created_by = models.ForeignKey(UserProfile,on_delete=models.CASCADE,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_by = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    is_deleted = models.BooleanField(default=False)
    status = models.BooleanField(default=True)

    class Meta:
        abstract = True



class Organization(BaseModel):
    organization_id = models.IntegerField(unique=True, editable=False)
    organization_name = models.CharField(max_length=250)
    organization_type = models.CharField(max_length=100)
    organization_logo = models.FileField(upload_to='media/',null=True)
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

class Role(models.Model):
    """Defines a role within an organization (e.g., Admin, Editor, Viewer)."""
    name = models.CharField(max_length=50)    
    description = models.TextField(blank=True, null=True)
    menu = models.ManyToManyField('Menu', through='RolePermission')
    

class UserDetails(models.Model):
    user = models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    role = models.ForeignKey(Role,on_delete=models.CASCADE,null=True)
    organization = models.ForeignKey(Organization,on_delete=models.CASCADE,null=True)
    resume = models.FileField(upload_to='resume/',null=True)
    created_by = models.CharField(max_length=100,null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_by = models.CharField(max_length=100,null=True)
    updated_at = models.DateTimeField(auto_now_add=True,null=True)


class OrganizationType(models.Model):
    name = models.CharField(max_length=100,null=True)
    description = models.TextField(null=True)


class Menu(models.Model):
    name = models.CharField(max_length=255)
    code = models.SlugField(unique=True)  # Unique code for internal reference (e.g., 'dashboard')
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    

    

class RolePermission(models.Model):
    """Defines specific permissions for a role on a menu (e.g., can_view, can_edit)."""
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE,null=True)
    can_view = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    class Meta:
        unique_together = ('role', 'menu')

    def __str__(self):
        return f"{self.role.name} - {self.menu.name} Permissions"


# @receiver(post_save, sender=UserProfile)
# def create_user_details(sender, instance, created, **kwargs):
#     if created:  # Check if this is a new instance
#         print(f"instance: {instance} kwargs: {kwargs}",flush=True)
#         try:
#             image_obj,created = ProfileImage.objects.get_or_create(user = instance,
#                                             image=kwargs.get('image')                                            
#                                             )
#             print("profile image created successfully",flush=True)
#             file_obj = FileUpload()
#             file_obj.s3_file_upload(file_path= image_obj.image) 

#             if kwargs.get('image'):
#                 print("uploaded successfully",flush=True) 
#                 os.remove(str(image_obj.image))           
            
#         except:
#             pass       
    
     
    
class MediaFile(models.Model):
    file = models.FileField(upload_to='media/')

    def __str__(self):
        return self.title
    

