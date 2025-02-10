from django.contrib import admin
from .models import Organization,Menu,Role  # Import your model

admin.site.register(Organization)  # Register the model
admin.site.register(Menu)
admin.site.register(Role)