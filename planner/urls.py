from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='overview'),

    path('event/create/', views.event_create, name='event_create'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),

    path('feed/', views.event_ics_feed, name='ics_feed'),

    path('contacts/', views.contacts_view, name='contacts'),
    path('contacts/<int:contact_id>', views.contacts_view, name='contact'),
    path('contacts/save/', views.contact_save, name='contact_create'),
    path('contacts/save/<int:contact_id>/', views.contact_save, name='contact_update'),

    path('tasks/', views.tasklists_view, name='tasklists'),
    path('tasks/save/', views.tasklist_save, name='tasklist_create'),
    path('tasks/save/<int:tasklist_id>/', views.tasklist_save, name='tasklist_update'),
    path('tasks/<int:tasklist_id>/', views.tasklist_detail, name='tasklist_detail'),

    path('tasks/<int:tasklist_id>/group/save/', views.taskgroup_save, name='taskgroup_create'),
    path('tasks/<int:tasklist_id>/group/save/<int:group_id>/', views.taskgroup_save, name='taskgroup_update'),

    path('tasks/<int:tasklist_id>/task/save/', views.task_save, name='task_create'),
    path('tasks/<int:tasklist_id>/task/save/<int:task_id>/', views.task_save, name='task_update'),
]
