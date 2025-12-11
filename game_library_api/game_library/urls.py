from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path, include
from django.views.generic import RedirectView, TemplateView
from rest_framework.routers import DefaultRouter
from library_app import views
from django.contrib.auth import views as auth_views


from library_app.views_bokeh import MonthlyRevenueBokehAPIView, GenrePlaytimeBokehAPIView, DeveloperRevenueBokehAPIView, \
    TopRatedGamesBokehAPIView, WhalesAnalysisBokehAPIView, UserGenreBreakdownAPIView, UserActivityBokehAPIView
from library_app.views_dashboard import DeveloperRevenueDashboardView, MonthlyRevenueDashboardView, \
    UserActivityDashboardView, \
    WhalesAnalysisDashboardView, GenrePlaytimeDashboardView, TopRatedGamesDashboardView, \
    MonthlyRevenueBokehDashboardView, GenrePlaytimeBokehDashboardView, DeveloperRevenueBokehDashboardView, \
    TopRatedGamesBokehDashboardView, WhalesAnalysisBokehDashboardView, UserActivityBokehDashboardView, PlotlyDashboardV1View, BokehDashboardV2View
from library_ui import views_api

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'libraries', views.LibraryViewSet, basename='library')
router.register(r'library-games', views.LibraryGameViewSet, basename='librarygame')
router.register(r'order-games', views.OrderGameViewSet, basename='ordergame')
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

    path('dashboard/', login_required(TemplateView.as_view(template_name='dashboard/menu.html')), name='dashboard-menu'),

    path('dashboard/v1/full/', PlotlyDashboardV1View.as_view(), name='plotly-dashboard-v1-full'),

    path('dashboard/v1/genre-playtime/', GenrePlaytimeDashboardView.as_view(), name='plotly-dashboard-v1-genre-playtime'),
    path('dashboard/v1/top-rated-games/', TopRatedGamesDashboardView.as_view(), name='plotly-dashboard-v1-top-rated-games'),
    path('dashboard/v1/dev-revenue/', DeveloperRevenueDashboardView.as_view(), name='plotly-dashboard-v1-dev-revenue'),
    path('dashboard/v1/monthly-revenue/', MonthlyRevenueDashboardView.as_view(), name='plotly-dashboard-v1-monthly-revenue'),
    path('dashboard/v1/user-activity/', UserActivityDashboardView.as_view(), name='plotly-dashboard-v1-user-activity'),
    path('dashboard/v1/whales-analysis/', WhalesAnalysisDashboardView.as_view(), name='plotly-dashboard-v1-whales-analysis'),

    path('dashboard/v2/full/', BokehDashboardV2View.as_view(), name='bokeh-dashboard-v2-full'),

    path('dashboard/v2/monthly-revenue/', MonthlyRevenueBokehDashboardView.as_view(), name='bokeh-dashboard-v2-monthly-revenue'),
    path('dashboard/v2/genre-playtime/', GenrePlaytimeBokehDashboardView.as_view(), name='bokeh-dashboard-v2-genre-playtime'),
    path('dashboard/v2/dev-revenue/', DeveloperRevenueBokehDashboardView.as_view(), name='bokeh-dashboard-v2-dev-revenue'),
    path('dashboard/v2/top-rated-games/', TopRatedGamesBokehDashboardView.as_view(), name='bokeh-dashboard-v2-top-rated-games'),
    path('dashboard/v2/whales-analysis/', WhalesAnalysisBokehDashboardView.as_view(), name='bokeh-dashboard-v2-whales-analysis'),
    path('dashboard/v2/user-activity/', UserActivityBokehDashboardView.as_view(), name='bokeh-dashboard-v2-user-activity'),

    path('api/reports/monthly-revenue-bokeh/', MonthlyRevenueBokehAPIView.as_view(), name='monthly_revenue_bokeh_api'),
    path('api/reports/genre-playtime-bokeh/', GenrePlaytimeBokehAPIView.as_view(), name='genre_playtime_bokeh_api'),
    path('api/reports/developer-revenue-bokeh/', DeveloperRevenueBokehAPIView.as_view(), name='developer_revenue_bokeh_api'),
    path('api/reports/top-rated-games-bokeh/', TopRatedGamesBokehAPIView.as_view(), name='top_rated_games_bokeh_api'),
    path('api/reports/whales-analysis-bokeh/', WhalesAnalysisBokehAPIView.as_view(), name='whales_analysis_bokeh_api'),
    path('api/reports/user-activity-bokeh/', UserActivityBokehAPIView.as_view(), name='user_activity_bokeh_api'),
    path('api/analysis/user-genre-breakdown/', UserGenreBreakdownAPIView.as_view(), name='user_genre_breakdown_api'),

    path('client/', include('library_ui.urls')),

    path('', RedirectView.as_view(pattern_name='login', permanent=False), name='index'),
]


