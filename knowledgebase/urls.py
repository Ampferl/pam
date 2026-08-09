from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='overview'),
    path('note/<int:item_id>/', views.index_view, name='note_detail'),
    path('item/create/', views.item_create_view, name='item_create'),
    path('item/<int:item_id>/update/', views.item_update_view, name='item_update'),
    path('item/<int:item_id>/rename/', views.item_rename_view, name='item_rename'),
    path('item/<int:item_id>/move/', views.item_move_view, name='item_move'),
    path('item/<int:item_id>/delete/', views.item_delete_view, name='item_delete'),
]
