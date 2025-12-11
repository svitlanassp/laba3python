from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

class DashboardView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    redirect_field_name = 'next'

class DeveloperRevenueDashboardView(DashboardView):
    def get(self, request, *args, **kwargs):
        return render(request, 'dashboard/developer_revenue_dashboard.html', {})

class MonthlyRevenueDashboardView(DashboardView):
    def get(self, request, *args, **kwargs):
        return render(request, 'dashboard/monthly_revenue_dashboard.html', {})

class UserActivityDashboardView(DashboardView):
    def get(self, request, *args, **kwargs):
        return render(request, 'dashboard/user_activity_dashboard.html', {})

class WhalesAnalysisDashboardView(DashboardView):
    def get(self, request, *args, **kwargs):
        return render(request, 'dashboard/whales_analysis_dashboard.html', {})

class GenrePlaytimeDashboardView(DashboardView):
    def get(self, request, *args, **kwargs):
        return render(request, 'dashboard/genre_playtime_dashboard.html', {})

class TopRatedGamesDashboardView(DashboardView):
    def get(self, request, *args, **kwargs):
        return render(request, 'dashboard/top_rated_games_dashboard.html', {})

class MonthlyRevenueBokehDashboardView(DashboardView):
    def get(self, request, *args, **kwargs):
        return render(request, 'dashboard/monthly_revenue_bokeh_dashboard.html', {})

class GenrePlaytimeBokehDashboardView(DashboardView):
    def get(self, request, *args, **kwargs):
        return render(request, 'dashboard/genre_playtime_bokeh_dashboard.html', {})

class DeveloperRevenueBokehDashboardView(DashboardView):
    def get(self, request, *args, **kwargs):
        return render(request, 'dashboard/developer_revenue_bokeh_dashboard.html', {})

class TopRatedGamesBokehDashboardView(DashboardView):
    def get(self, request, *args, **kwargs):
        return render(request, 'dashboard/top_rated_games_bokeh_dashboard.html', {})

class WhalesAnalysisBokehDashboardView(DashboardView):
    def get(self, request, *args, **kwargs):
        return render(request, 'dashboard/whales_analysis_bokeh_dashboard.html', {})

class UserActivityBokehDashboardView(DashboardView):
    def get(self, request, *args, **kwargs):
        return render(request, 'dashboard/user_activity_bokeh_dashboard.html', {})

class PlotlyDashboardV1View(DashboardView):
    def get(self, request, *args, **kwargs):
        context = {
            'available_years': list(range(2020, 2026))
        }
        return render(request, 'dashboard/plotly_dashboard_v1.html', context)

class BokehDashboardV2View(DashboardView):
    def get(self, request, *args, **kwargs):
        return render(request, 'dashboard/bokeh_dashboard_v2.html', {})