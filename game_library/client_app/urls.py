from django.urls import path
from . import views_native, views_api
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('api/games/', views_api.api_list_games, name='api_list_games'),
    path('api/games/delete/<int:pk>/', views_api.api_delete_game, name='api_delete_game'),

    path('api/developers/', views_api.api_list_developers, name='api_list_developers'),
    path('api/developers/delete/<int:pk>/', views_api.api_delete_developer, name='api_delete_developer'),
  
    path('games/', views_native.native_list, name='native_list'),
    path('games/new/', views_native.native_edit, name='native_create'),
    path('games/<int:pk>/', views_native.native_detail, name='native_detail'),
    path('games/<int:pk>/edit/', views_native.native_edit, name='native_edit'),
    path('games/<int:pk>/delete/', views_native.native_delete, name='native_delete'),

    path('login/', auth_views.LoginView.as_view(template_name='client_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='native_list'), name='logout'),

    path('my-library/', views_native.native_library, name='native_library'),
    path('add-balance/', views_native.add_balance, name='add_balance'),
    path('buy/<int:pk>/', views_native.buy_game, name='buy_game'),
    path('return/<int:pk>/', views_native.return_game, name='return_game'),

]
