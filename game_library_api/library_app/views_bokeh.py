from rest_framework.response import Response
from rest_framework.views import APIView
import pandas as pd

from library_app.repositories.repository_manager import RepositoryManager
from library_app.serializers import MonthlyRevenueReportSerializer, GenrePlaytimeReportSerializer, \
    DeveloperRevenueReportSerializer, TopRatedGameSerializer, WhalesGenreBreakdownSerializer, \
    UserSpendingRankSerializer, UserActivityReportSerializer
from .utils import generate_monthly_revenue_bokeh_chart, generate_genre_playtime_bokeh_chart, \
    generate_developer_revenue_bokeh_chart, generate_top_rated_games_bokeh_chart, generate_whales_analysis_bokeh_charts, \
    generate_user_activity_bokeh_charts

repo_manager = RepositoryManager()

class MonthlyRevenueBokehAPIView(APIView):
    def get(self, request, *args, **kwargs):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        report_data_qs = repo_manager.orders.get_monthly_revenue_report(
            start_date_str=start_date,
            end_date_str=end_date
        )

        serializer = MonthlyRevenueReportSerializer(report_data_qs, many=True)
        list_of_dicts = serializer.data
        script, div = generate_monthly_revenue_bokeh_chart(list_of_dicts)

        return Response({
            "script": script,
            "div": div
        })

class GenrePlaytimeBokehAPIView(APIView):
    def get(self, request, *args, **kwargs):
        min_unique_games_str = request.query_params.get('min_unique_games', '5')
        try:
            min_games = int(min_unique_games_str)
        except ValueError:
            min_games = 5
        report_data_qs = repo_manager.genres.get_top_genres_by_playtime(min_games_count=min_games)

        serializer = GenrePlaytimeReportSerializer(report_data_qs, many=True)
        list_of_dicts = serializer.data
        script, div = generate_genre_playtime_bokeh_chart(list_of_dicts)

        return Response({
            "script": script,
            "div": div
        })


class DeveloperRevenueBokehAPIView(APIView):
    """
    Повертає компоненти Bokeh для графіку рейтингу розробників за доходом.
    """

    def get(self, request, *args, **kwargs):
        year = request.query_params.get('year')
        top_n_str = request.query_params.get('top_n', '10')

        report_data_all_qs = repo_manager.developers.get_revenue_report(year=year)

        serializer = DeveloperRevenueReportSerializer(report_data_all_qs, many=True)
        list_of_dicts = serializer.data
        if list_of_dicts:
            df = pd.DataFrame(list_of_dicts)
            try:
                top_n = int(top_n_str)
                list_of_dicts = df.head(top_n).to_dict('records')
            except ValueError:
                pass
        script, div = generate_developer_revenue_bokeh_chart(list_of_dicts)

        return Response({
            "script": script,
            "div": div
        })


class TopRatedGamesBokehAPIView(APIView):
    def get(self, request, *args, **kwargs):
        min_reviews_str = request.query_params.get('min_reviews', '10')
        genre_name = request.query_params.get('genre')
        min_price_str = request.query_params.get('min_price')
        max_price_str = request.query_params.get('max_price')

        top_n = 30

        try:
            min_reviews = int(min_reviews_str)
            min_price = float(min_price_str) if min_price_str else None
            max_price = float(max_price_str) if max_price_str else None
        except ValueError:
            min_reviews = 10
            min_price = None
            max_price = None

        report_data_qs = repo_manager.games.get_top_rated_games_report(
            min_reviews=min_reviews,
            genre_name=genre_name,
            min_price=min_price,
            max_price=max_price
        )
        serializer = TopRatedGameSerializer(report_data_qs, many=True)
        list_of_dicts = serializer.data

        script, div = generate_top_rated_games_bokeh_chart(list_of_dicts, top_n=top_n)

        return Response({
            "script": script,
            "div": div
        })


class UserGenreBreakdownAPIView(APIView):
    def get(self, request, *args, **kwargs):
        user_ids_str = request.query_params.get('user_ids')

        if not user_ids_str:
            return Response([])

        selected_user_ids = [int(uid) for uid in user_ids_str.split(',') if uid.isdigit()]

        genre_breakdown_qs = repo_manager.users.get_whales_genre_breakdown(selected_user_ids)

        breakdown_serializer = WhalesGenreBreakdownSerializer(genre_breakdown_qs, many=True)

        return Response(breakdown_serializer.data)

class WhalesAnalysisBokehAPIView(APIView):
    def get(self, request, *args, **kwargs):
        year = request.query_params.get('year')
        top_n_str = request.query_params.get('top_n', 10)

        try:
            top_n = int(top_n_str)
        except ValueError:
            top_n = 10

        spending_rank_qs = repo_manager.users.get_spending_rank(year=year)
        spending_rank_data = spending_rank_qs[:top_n]
        rank_serializer = UserSpendingRankSerializer(spending_rank_data, many=True)
        rank_list = rank_serializer.data

        selected_user_ids = [user['id'] for user in rank_list]

        genre_breakdown_qs = repo_manager.users.get_whales_genre_breakdown(selected_user_ids)
        breakdown_serializer = WhalesGenreBreakdownSerializer(genre_breakdown_qs, many=True)
        genre_list = breakdown_serializer.data

        script, div = generate_whales_analysis_bokeh_charts(rank_list, genre_list)

        return Response({
            "script": script,
            "div": div
        })


class UserActivityBokehAPIView(APIView):

    def get(self, request, *args, **kwargs):
        min_playtime_str = request.query_params.get('min_playtime', 0)
        top_n_str = request.query_params.get('top_n')

        report_data_qs = repo_manager.users.get_user_activity_report()
        serializer = UserActivityReportSerializer(report_data_qs, many=True)
        list_of_dicts = serializer.data

        df = pd.DataFrame(list_of_dicts)
        correlation = None

        if not df.empty:
            df['total_playtime'] = pd.to_numeric(df['total_playtime'], errors='coerce')
            df['games_owned'] = pd.to_numeric(df['games_owned'], errors='coerce')
            df.dropna(subset=['total_playtime', 'games_owned'], inplace=True)

            try:
                min_playtime = int(min_playtime_str)
                df = df[df['total_playtime'] >= min_playtime]
            except ValueError:
                pass

            if not df.empty:
                if df[['total_playtime', 'games_owned']].notna().all().all():
                    correlation_matrix = df[['total_playtime', 'games_owned']].corr()
                    correlation = round(correlation_matrix.loc['total_playtime', 'games_owned'], 4)

            if top_n_str:
                try:
                    top_n = int(top_n_str)
                    df_filtered = df.sort_values(by='total_playtime', ascending=False).head(top_n)
                except ValueError:
                    df_filtered = df
            else:
                df_filtered = df
        else:
            df_filtered = pd.DataFrame()

        activity_data_dicts_filtered = df_filtered.to_dict('records')

        script, div = generate_user_activity_bokeh_charts(activity_data_dicts_filtered, correlation)

        return Response({
            "script": script,
            "div": div
        })