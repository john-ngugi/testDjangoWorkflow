from django.urls import path
from . import views

urlpatterns =[
    path('',views.home,name="indexpage"),
    path('loading',views.loading, name="loading"),
    path('home/',views.newIndex,name='index'),
    path('layers/',views.index,name="home"),
    path('layers/get-layer/',views.getLayers,name="getLayer"),
    path('get_marker_info/', views.get_marker_info, name='get_marker_info'),
    path('getandcreatesatistisfaction/',views.getMarkerInfoFromModel, name='get_and_create_satisfaction'),
    path('research/', views.getResearch,name='get_research'),
    path('research-paper/<str:paper_name>/',views.getResearchPaper, name='research_paper'),
    path('search_research/', views.searchResearch, name='search-research'),
    path('notebooklist/', views.notebook_list, name='notebook_list'),
    path('<int:pk>/', views.notebook_detail, name='notebook_detail'),
]
