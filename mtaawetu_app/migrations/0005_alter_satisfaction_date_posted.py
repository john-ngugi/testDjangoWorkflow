# Generated by Django 5.0.6 on 2024-07-13 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mtaawetu_app', '0004_satisfaction_date_posted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='satisfaction',
            name='date_posted',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]