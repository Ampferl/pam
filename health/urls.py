from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='overview'),
    path('garmin/sync/', views.garmin_sync_view, name='garmin_sync'),
]
