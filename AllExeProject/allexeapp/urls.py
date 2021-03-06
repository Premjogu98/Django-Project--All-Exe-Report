from . import views
from django.urls import path

urlpatterns = [
    path('homepage',views.index , name='homepage'),
    path('source-list',views.source_list , name='source-list'),
    path('Add-source',views.Add_source , name='Add-source'),
    path('load-data-on-model',views.loadmodel_data , name='load-data-on-model'),
    path('update-model-data',views.update_model , name='update-model-data'),
    path('source-details',views.source_details , name='source-details'),
    # path('All-source-details',views.All_source_details , name='All-source-details'),
    path('export-to-csv',views.Export_csv , name='export-to-csv'),
    path('Zero-count-page',views.zero_count , name='Zero-count-page'),
    path('Send-email',views.Send_email , name='Send-email'),
    path('QC-Detail',views.QC_Detail , name='QC-Detail'),
    path('Login-page',views.Login_page , name='Login-page'),
    path('Logout',views.Logout , name='Logout'),



]