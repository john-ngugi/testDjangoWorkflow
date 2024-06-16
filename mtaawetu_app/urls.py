from django.urls import path
from . import views

urlpatterns =[
    path('',views.index, name="home"),
    path('get-layer/',views.getLayers,name="getLayer"),
]
