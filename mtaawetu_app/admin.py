from django.contrib import admin
from .models import Amenities,Satisfaction,Research
# Register your models here.


admin.site.register(Amenities)
admin.site.register(Satisfaction)
admin.site.register(Research)


class AmenitiesAdmin(admin.ModelAdmin):
    list_display = ("name", "amenity_type")
