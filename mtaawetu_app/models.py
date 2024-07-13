from django.db import models
from django.utils import timezone

# Create your models here.


class Amenities(models.Model):
    name = models.CharField(max_length=250)
    # lat = models.DecimalField()
    # lon = models.DecimalField()
    amenity_type = models.CharField(max_length=250,null=True)


    def __str__(self):
        return self.name
    class Meta:
        app_label = 'mtaawetu_app'

class Satisfaction(models.Model):
    amenity = models.ForeignKey(Amenities, on_delete=models.CASCADE)
    comment = models.TextField(max_length=250)
    satisfaction_range = models.IntegerField()
    date_posted = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-comment"]
        app_label = 'mtaawetu_app'
    def __str__(self):
        return self.amenity.name
