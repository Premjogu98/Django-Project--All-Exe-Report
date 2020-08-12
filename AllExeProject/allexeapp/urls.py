from . import views
from django.urls import path

urlpatterns = [
    path('homepage',views.index , name='homepage'),
    path('source-list',views.source_list , name='source-list'),
    path('Add-source',views.Add_source , name='Add-source'),
    path('load-data-on-model',views.loadmodel_data , name='load-data-on-model'),
    path('update-model-data',views.update_model , name='update-model-data'),
    path('source-details',views.source_details , name='source-details'),
    path('All-source-details',views.All_source_details , name='All-source-details'),

]