from django.urls import path
from . import views_api, views_dashboard

urlpatterns = [
    path('games/', views_api.game_list_view, name='game_list'),
    path('games/<int:pk>/', views_api.game_detail_view, name='game_detail'),
    path('buy/<int:pk>/', views_api.buy_game_view, name='buy_game'),
    path('top-up/', views_api.top_up_balance_view, name='top_up'),
    path('library/', views_api.library_view, name='library'),
    path('dashboard/playtime/', views_dashboard.playtime_dashboard_view, name='playtime_dashboard'),
]