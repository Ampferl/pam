from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='overview'),

    path('event/create/', views.event_create, name='event_create'),
    path('event/update/<int:event_id>/', views.event_update, name='event_update'),

    path('feed/', views.event_ics_feed, name='ics_feed'),

    path('contacts/', views.contacts_view, name='contacts'),
    path('contacts/<int:contact_id>', views.contacts_view, name='contact'),
    path('contacts/save/', views.contact_save, name='contact_create'),
    path('contacts/save/<int:contact_id>/', views.contact_save, name='contact_update'),
]
