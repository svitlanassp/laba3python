# client_app/urls.py

from django.urls import path
from . import views_native, views_api # <--- Імпортуємо обидва файли

urlpatterns = [
    # Частина А (native)
    # path('native/', views_native.native_list, name='native_list'),
    # path('native/create/', views_native.native_create, name='native_create'),
    #
    # # Частина Б (api client)
    # path('api-client/', views_api.api_list, name='api_list'),
    # path('api-client/create/', views_api.api_create, name='api_create'),
]