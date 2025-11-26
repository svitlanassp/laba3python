# client_app/urls.py

from django.urls import path
from . import views_native, views_api # <--- Імпортуємо обидва файли

urlpatterns = [
    # Частина А (native)
    # path('native/', views_native.native_list, name='native_list'),
    # path('native/create/', views_native.native_create, name='native_create'),
    #
    # # Частина Б (api client)
    path('games/', views_api.api_list_games, name='api_list_games'),
    path('games/delete/<int:pk>/', views_api.api_delete_game, name='api_delete_game'),

    path('developers/', views_api.api_list_developers, name='api_list_developers'),
    path('developers/delete/<int:pk>/', views_api.api_delete_developer, name='api_delete_developer'),
]