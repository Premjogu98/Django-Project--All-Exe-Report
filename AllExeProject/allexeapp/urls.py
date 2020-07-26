from . import views
from django.urls import path

urlpatterns = [
    path('homepage',views.index , name='homepage'),
    path('source-list',views.source_list , name='source-list'),
    path('Add-source',views.Add_source , name='Add-source'),
]