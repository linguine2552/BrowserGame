# /backend/game_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('initialize/', views.initialize_game, name='initialize_game'),
    path('save-map/', views.save_map, name='save_map'),    
]