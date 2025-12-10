from django.shortcuts import render
from django.views import View

class DeveloperRevenueDashboardView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'dashboard/developer_revenue_dashboard.html', {})

class MonthlyRevenueDashboardView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'dashboard/monthly_revenue_dashboard.html', {})

class UserActivityDashboardView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'dashboard/user_activity_dashboard.html', {})

class WhalesAnalysisDashboardView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'dashboard/whales_analysis_dashboard.html', {})

class GenrePlaytimeDashboardView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'dashboard/genre_playtime_dashboard.html', {})

class TopRatedGamesDashboardView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'dashboard/top_rated_games_dashboard.html', {})

class MonthlyRevenueBokehDashboardView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'dashboard/monthly_revenue_bokeh_dashboard.html', {})

class GenrePlaytimeBokehDashboardView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'dashboard/genre_playtime_bokeh_dashboard.html', {})

class DeveloperRevenueBokehDashboardView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'dashboard/developer_revenue_bokeh_dashboard.html', {})

class TopRatedGamesBokehDashboardView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'dashboard/top_rated_games_bokeh_dashboard.html', {})

class WhalesAnalysisBokehDashboardView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'dashboard/whales_analysis_bokeh_dashboard.html', {})

class UserActivityBokehDashboardView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'dashboard/user_activity_bokeh_dashboard.html', {})