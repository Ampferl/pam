from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('settings', views.settings_view, name='settings'),
    path('settings/feed-token/regenerate', views.regenerate_feed_token, name='regenerate_feed_token'),
]
