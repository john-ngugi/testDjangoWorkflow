from django.contrib import admin
from .models import Amenities,Satisfaction
# Register your models here.


admin.site.register(Amenities)
admin.site.register(Satisfaction)

class AmenitiesAdmin(admin.ModelAdmin):
    list_display = ("name", "amenity_type")
