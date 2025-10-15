from django.urls import path
from . import views

urlpatterns = [
    path('hosts/', views.hosts_list_page, name='hosts_page'),
    path('hosts.json', views.hosts_list_json, name='hosts_json'),
    path('scan_status.json', views.scan_status, name='scan_status'),
    path('start_scan/', views.start_scan, name='start_scan'),
]