from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='overview'),
    path('management/', views.management_view, name='management_overview'),
]
