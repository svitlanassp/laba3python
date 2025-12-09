from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter
from library_app import views
from django.contrib.auth import views as auth_views
from library_ui import views_api

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'libraries', views.LibraryViewSet, basename='library')
router.register(r'library-games', views.LibraryGameViewSet, basename='librarygame')
router.register(r'order-games',views.OrderGameViewSet, basename='ordergame')
router.register(r'games', views.GameViewSet, basename='game')
router.register(r'developers', views.DeveloperViewSet, basename='developer')
router.register(r'publishers', views.PublisherViewSet, basename='publisher')
router.register(r'genres', views.GenreViewSet, basename='genre')
router.register(r'game-genres', views.GameGenreViewSet, basename='gamegenre')
router.register(r'reviews', views.ReviewViewSet, basename='review')
router.register(r'analytics', views.AnalyticsViewSet, basename='analytics')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),

    path('accounts/login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('accounts/logout/', views_api.user_logout, name='logout'),

    path('client/', include('library_ui.urls')),
    path('', RedirectView.as_view(pattern_name='login', permanent=False), name='index'),

]