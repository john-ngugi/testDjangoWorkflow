from django.contrib import admin
from .models import Amenities,Satisfaction,Research,Notebook
# Register your models here.


admin.site.register(Amenities)
admin.site.register(Satisfaction)
admin.site.register(Research)
admin.site.register(Notebook)

class AmenitiesAdmin(admin.ModelAdmin):
    list_display = ("name", "amenity_type")
