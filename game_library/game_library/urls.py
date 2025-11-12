from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from library_app.views import *

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'libraries', LibraryViewSet, basename='library')
router.register(r'library-games', LibraryGameViewSet, basename='librarygame')
router.register(r'order-games',OrderGameViewSet, basename='ordergame')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
