from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from library_app import views

router = DefaultRouter()
router.register(r'games', views.GameViewSet, basename='game')
router.register(r'developers', views.DeveloperViewSet, basename='developer')
router.register(r'publishers', views.PublisherViewSet, basename='publisher')
router.register(r'genres', views.GenreViewSet, basename='genre')
router.register(r'game-genres', views.GameGenreViewSet, basename='gamegenre')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
