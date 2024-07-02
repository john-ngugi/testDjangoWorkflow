from django.urls import path
from . import views

urlpatterns =[
    path('',views.home,name="indexpage"),
    path('loading',views.loading, name="loading"),
    path('home/',views.newIndex,name='index'),
    path('layers/',views.index,name="home"),
    path('layers/get-layer/',views.getLayers,name="getLayer"),
]
