from django.urls import path
from . import views

urlpatterns =[
    path('',views.loading, name="loading"),
    path('home/',views.newIndex,name='index'),
    path('layers/',views.index,name="home"),
    path('get-layer/',views.getLayers,name="getLayer"),
]
