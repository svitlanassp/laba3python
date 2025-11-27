from django.urls import path
from . import views_native, views_api

urlpatterns = [
    path('games/', views_native.native_list, name='native_list'),
    path('games/new/', views_native.native_edit, name='native_create'),
    path('games/<int:pk>/', views_native.native_detail, name='native_detail'),
    path('games/<int:pk>/edit/', views_native.native_edit, name='native_edit'),
    path('games/<int:pk>/delete/', views_native.native_delete, name='native_delete'),
]