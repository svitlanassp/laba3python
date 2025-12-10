from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter
from library_app import views
from django.contrib.auth import views as auth_views


from library_app.views_bokeh import MonthlyRevenueBokehAPIView, GenrePlaytimeBokehAPIView, DeveloperRevenueBokehAPIView, \
    TopRatedGamesBokehAPIView, WhalesAnalysisBokehAPIView, UserGenreBreakdownAPIView, UserActivityBokehAPIView
from library_app.views_dashboard import DeveloperRevenueDashboardView, MonthlyRevenueDashboardView, \
    UserActivityDashboardView, \
    WhalesAnalysisDashboardView, GenrePlaytimeDashboardView, TopRatedGamesDashboardView, \
    MonthlyRevenueBokehDashboardView, GenrePlaytimeBokehDashboardView, DeveloperRevenueBokehDashboardView, \
    TopRatedGamesBokehDashboardView, WhalesAnalysisBokehDashboardView, UserActivityBokehDashboardView
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
router.register(r'reports', views.ReportViewSet, basename='report')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),

    path('accounts/login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('accounts/logout/', views_api.user_logout, name='logout'),


    path('dashboard/genre-playtime/', GenrePlaytimeDashboardView.as_view(), name='genre-playtime'),
    path('dashboard/top-rated-games/', TopRatedGamesDashboardView.as_view(), name='top-rated-games'),
    path('dashboard/dev-revenue/', DeveloperRevenueDashboardView.as_view(), name='dev_revenue_dashboard'),
    path('dashboard/monthly-revenue/', MonthlyRevenueDashboardView.as_view(), name='monthly_revenue_dashboard'),
    path('dashboard/user-activity/', UserActivityDashboardView.as_view(), name='user_activity_dashboard'),
    path('dashboard/whales-analysis/', WhalesAnalysisDashboardView.as_view(), name='whales_analysis_dashboard'),
path('api/reports/top-rated-games-bokeh/', TopRatedGamesBokehAPIView.as_view(), name='top_rated_games_bokeh_api'),
path('api/reports/developer-revenue-bokeh/', DeveloperRevenueBokehAPIView.as_view(), name='developer_revenue_bokeh_api'),
    path('api/reports/genre-playtime-bokeh/', GenrePlaytimeBokehAPIView.as_view(), name='genre_playtime_bokeh_api'),
    path('api/reports/monthly-revenue-bokeh/', MonthlyRevenueBokehAPIView.as_view(), name='monthly_revenue_bokeh_api'),
    path('dashboard/monthly-revenue-bokeh/', MonthlyRevenueBokehDashboardView.as_view(), name='monthly_revenue_bokeh_dashboard'),
    path('dashboard/genre-playtime-bokeh/', GenrePlaytimeBokehDashboardView.as_view(), name='genre_playtime_bokeh_dashboard'),
    path('dashboard/dev-revenue-bokeh/', DeveloperRevenueBokehDashboardView.as_view(), name='developer_revenue_bokeh_dashboard'),
path('dashboard/top-rated-games-bokeh/', TopRatedGamesBokehDashboardView.as_view(), name='top_rated_games_bokeh_dashboard'), # <--- НОВИЙ ШЛЯХ


    path('api/reports/whales-analysis-bokeh/', WhalesAnalysisBokehAPIView.as_view(), name='whales_analysis_bokeh_api'),
    path('api/analysis/user-genre-breakdown/', UserGenreBreakdownAPIView.as_view(), name='user_genre_breakdown_api'),

path('api/reports/user-activity-bokeh/', UserActivityBokehAPIView.as_view(), name='user-activity-bokeh'),


    path('dashboard/whales-analysis-bokeh/', WhalesAnalysisBokehDashboardView.as_view(), name='whales_analysis_bokeh_dashboard'),
path('dashboard/user-activity-bokeh/', UserActivityBokehDashboardView.as_view(),name='user_activity_bokeh_dashboard'),
    path('client/', include('library_ui.urls')),
    path('', RedirectView.as_view(pattern_name='login', permanent=False), name='index'),

]