# Generated by Django 5.0.6 on 2024-07-11 05:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mtaawetu_app', '0002_alter_satisfaction_satisfaction_range'),
    ]

    operations = [
        migrations.AddField(
            model_name='amenities',
            name='amenity_type',
            field=models.CharField(max_length=250, null=True),
        ),
    ]
