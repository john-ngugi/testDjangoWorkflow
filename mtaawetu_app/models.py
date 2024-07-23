from django.db import models
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField
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

class Research(models.Model):
    title = models.CharField(max_length=50,blank=True)
    Author = models.CharField(max_length=200)
    source = models.CharField(max_length=1000)
    blob = models.ImageField(upload_to='uploads',blank=True)
    body = RichTextUploadingField()

    def __str__(self):
        return self.title

class Notebook(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='notebooks/')

    def __str__(self):
        return self.title
