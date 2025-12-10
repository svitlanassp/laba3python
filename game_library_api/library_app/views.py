from decimal import Decimal
import pandas as pd

from django.db import transaction
from django.shortcuts import render
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from library_app.repositories.repository_manager import RepositoryManager
from .serializers import (
    GameSerializer, DeveloperSerializer,
    PublisherSerializer, GenreSerializer, GameGenreSerializer,
    UserSerializer, LibrarySerializer, OrderSerializer,
    LibraryGameSerializer, OrderGameSerializer, ReviewSerializer,
    GenrePlaytimeReportSerializer, MonthlyRevenueReportSerializer, DeveloperRevenueReportSerializer,
    UserActivityReportSerializer, UserSpendingRankSerializer, WhalesGenreBreakdownSerializer, TopRatedGameSerializer
)

repo_manager = RepositoryManager()

class BaseViewSet(viewsets.ViewSet):
    repo = None
    serializer_class = None
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request):
        items = self.repo.get_all()
        serializer = self.serializer_class(items, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        item = self.repo.get_by_id(pk)
        if not item:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(item)
        return Response(serializer.data)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            obj = self.repo.create(**serializer.validated_data)
            return Response(self.serializer_class(obj).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        item = self.repo.get_by_id(pk)
        if not item:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(item, data=request.data, partial=True)
        if serializer.is_valid():
            obj = self.repo.update(pk, **serializer.validated_data)
            return Response(self.serializer_class(obj).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        deleted = self.repo.delete(pk)
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)

class UserViewSet(BaseViewSet):
    repo = repo_manager.users
    serializer_class = UserSerializer

    @action(detail=True, methods=['get'])
    def data(self, request, pk=None):
        try:
            user = self.repo.get_by_id(pk)
        except Exception:
            return Response({'error': 'Некоректний ідентифікатор користувача.'}, status=status.HTTP_404_NOT_FOUND)

        if not user:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response({
            'user_id': user.pk,
            'username': user.username,
            'balance': user.balance
        })



    @action(detail=True, methods=['post'])
    def top_up(self, request, pk=None):
        amount = request.data.get('amount')

        try:
            amount = Decimal(amount)
            if amount <= 0:
                return Response({'error': 'Сума поповнення повинна бути позитивною.'},
                                status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError):
            return Response({'error': 'Некоректна сума.'},
                            status=status.HTTP_400_BAD_REQUEST)

        user = self.repo.get_by_id(pk)
        if not user:
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            with transaction.atomic():
                new_balance = user.balance + amount

                updated_user = self.repo.update(user.pk, balance=new_balance)

                return Response({
                    'message': f'Баланс успішно поповнено на {amount} $',
                    'new_balance': updated_user.balance
                }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': f'Помилка поповнення: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GameViewSet(BaseViewSet):
    repo = repo_manager.games
    serializer_class = GameSerializer

    def list(self, request):
        items = self.repo.get_all()

        user_owned_game_ids = set()

        if request.user.is_authenticated:
            user_owned_game_ids = repo_manager.library_games.get_owned_game_ids_by_user(request.user.id)

        serializer = self.serializer_class(
            items,
            many=True,
            context={'user_owned_game_ids': user_owned_game_ids}
        )
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def is_owned(self, request, pk=None):
        user_id_str = request.query_params.get('user_id')

        if not user_id_str:
            return Response({"error": "Потрібен параметр user_id."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_id = int(user_id_str)
            game_id = int(pk)
        except ValueError:
            return Response({"error": "ID користувача та гри мають бути цілими числами."},
                            status=status.HTTP_400_BAD_REQUEST)

        if not repo_manager.users.get_by_id(user_id):
            return Response({"error": "Користувача не знайдено."}, status=status.HTTP_404_NOT_FOUND)

        is_owned = self.repo.check_if_user_owns_game(user_id, game_id)

        return Response({'is_owned': is_owned})

    @action(detail=False, methods=['post'], url_path='buy')
    def buy_game(self, request):
        user_id = request.data.get('user_id')
        game_id = request.data.get('game_id')

        try:
            user = repo_manager.users.get_by_id(user_id)
            game = repo_manager.games.get_by_id(game_id)
        except Exception:
            return Response({'error': 'Некоректний формат ID.'}, status=status.HTTP_400_BAD_REQUEST)

        if not user or not game:
            return Response({'error': 'Користувача або гру не знайдено.'}, status=status.HTTP_404_NOT_FOUND)

        library = repo_manager.libraries.get_by_user(user)
        if library:
            if repo_manager.library_games.is_game_in_library(library.pk, game.pk):
                return Response({'error': f'Гра "{game.title}" вже є у вашій бібліотеці.'},
                                status=status.HTTP_400_BAD_REQUEST)

        if user.balance < game.price:
            return Response({'error': 'Недостатньо коштів на балансі.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                user.balance -= game.price
                repo_manager.users.update(user.pk, balance=user.balance)

                order_obj = repo_manager.orders.create(user=user, total_amount=game.price, status='complete')
                repo_manager.order_games.create(order=order_obj, game=game, price_at_purchase=game.price)

                if not library:
                    library = repo_manager.libraries.create(user=user)

                repo_manager.library_games.create(
                    library=library,
                    game=game,
                    purchase_date=timezone.now()
                )

            return Response({
                'message': f'Гра "{game.title}" успішно куплена!',
                'new_balance': user.balance
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': f'Помилка транзакції: {type(e).__name__}: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class OrderViewSet(BaseViewSet):
    repo = repo_manager.orders
    serializer_class = OrderSerializer



class LibraryViewSet(BaseViewSet):
    repo = repo_manager.libraries
    serializer_class = LibrarySerializer

    def list(self, request):
        user_id = request.query_params.get('user')

        if user_id:
            try:
                library = self.repo.get_by_user(user_id)

                if library:
                    serializer = self.serializer_class(library)
                    return Response([serializer.data])
                else:
                    return Response([])

            except Exception as e:
                return Response({'error': f'Некоректний ID користувача для фільтрації: {e}'},
                                status=status.HTTP_400_BAD_REQUEST)

        return super().list(request)

class LibraryGameViewSet(BaseViewSet):
    repo = repo_manager.library_games
    serializer_class = LibraryGameSerializer


class OrderGameViewSet(BaseViewSet):
    repo = repo_manager.order_games
    serializer_class = OrderGameSerializer


class DeveloperViewSet(BaseViewSet):
    repo = repo_manager.developers
    serializer_class = DeveloperSerializer


class PublisherViewSet(BaseViewSet):
    repo = repo_manager.publishers
    serializer_class = PublisherSerializer

class GenreViewSet(BaseViewSet):
    repo = repo_manager.genres
    serializer_class = GenreSerializer

class GameGenreViewSet(BaseViewSet):
    repo = repo_manager.game_genres
    serializer_class = GameGenreSerializer

class ReviewViewSet(BaseViewSet):
    repo = repo_manager.reviews
    serializer_class = ReviewSerializer

    @action(detail=False, methods=['get'])
    def by_game(self,request):
        game_id = request.query_params.get('game_id')
        if not game_id:
            return Response({'error'},status=status.HTTP_400_BAD_REQUEST)
        try:
            reviews = self.repo.get_reviews_by_game(game_id)
            serializer = self.serializer_class(reviews,many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': f'Помилка: {e}'}, status=status.HTTP_400_BAD_REQUEST)


class ReportViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['get'], url_path='genre-playtime')
    def playtime_ranking(self, request):
        min_unique_games_str = request.query_params.get('min_unique_games', '5')

        try:
            min_games = int(min_unique_games_str)
        except ValueError:
            min_games = 5

        report_data_qs = repo_manager.genres.get_top_genres_by_playtime(min_games_count=min_games)

        serializer = GenrePlaytimeReportSerializer(report_data_qs, many=True)
        list_of_dicts = serializer.data

        df = pd.DataFrame(list_of_dicts)
        analytics_stats = {}

        if not df.empty:
            df['avg_playtime_per_copy'] = pd.to_numeric(df['avg_playtime_per_copy'], errors='coerce')
            df['unique_game_count'] = pd.to_numeric(df['unique_game_count'], errors='coerce')

            analytics_stats = {
                "mean_avg_playtime": round(df['avg_playtime_per_copy'].mean(), 2),
                "max_avg_playtime": round(df['avg_playtime_per_copy'].max(), 2),
                "min_avg_playtime": round(df['avg_playtime_per_copy'].min(), 2),
                "median_avg_playtime": round(df['avg_playtime_per_copy'].median(), 2),
                "total_genres_in_report": df.shape[0],
                "total_unique_games": df['unique_game_count'].sum(),
            }

        return Response({
            "report_name": f"Top Genres by Playtime (Min Unique Games: {min_games})",
            "time_series_data": list_of_dicts,
            "analytics_stats": analytics_stats
        })

    @action(detail=False, methods=['get'], url_path='dev-revenue')
    def developer_revenue_report(self, request):
        year = request.query_params.get('year')
        top_n_str = request.query_params.get('top_n', 10)
        report_data_all_qs = repo_manager.developers.get_revenue_report(year=year)

        serializer = DeveloperRevenueReportSerializer(report_data_all_qs, many=True)
        list_of_dicts = serializer.data

        df = pd.DataFrame(list_of_dicts)
        analytics_stats = {}

        if not df.empty:
            df['total_revenue'] = pd.to_numeric(df['total_revenue'], errors='coerce')
            df['avg_price'] = pd.to_numeric(df['avg_price'], errors='coerce')

            analytics_stats = {
                "mean_revenue": round(df['total_revenue'].mean(), 2),
                "median_revenue": round(df['total_revenue'].median(), 2),
                "max_revenue": round(df['total_revenue'].max(), 2),
                "min_revenue": round(df['total_revenue'].min(), 2),
                "avg_price_mean": round(df['avg_price'].mean(), 2),
                "total_developers_count": df.shape[0],
            }

        top_n_data = []
        try:
            top_n = int(top_n_str)
            top_n_data = df.head(top_n).to_dict('records')
        except ValueError:
            top_n_data = df.to_dict('records')

        return Response({
            "report_name": f"Developer Revenue Report (Top {top_n})",
            "developer_data": top_n_data,
            "analytics_stats": analytics_stats
        })

    @action(detail=False, methods=['get'], url_path='monthly-revenue')
    def monthly_revenue_report(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        report_data_qs = repo_manager.orders.get_monthly_revenue_report(
            start_date_str=start_date,
            end_date_str=end_date
        )

        serializer = MonthlyRevenueReportSerializer(report_data_qs, many=True)
        list_of_dicts = serializer.data

        df = pd.DataFrame(list_of_dicts)
        analytics_stats = {}

        if not df.empty:
            df['total_revenue'] = pd.to_numeric(df['total_revenue'], errors='coerce')

            analytics_stats = {
                "total_period_revenue": round(df['total_revenue'].sum(), 2),
                "mean_monthly_revenue": round(df['total_revenue'].mean(), 2),
                "max_monthly_revenue": round(df['total_revenue'].max(), 2),
                "months_in_report": df.shape[0],
            }

        return Response({
            "report_name": f"Monthly Revenue ({start_date or 'Start'} to {end_date or 'End'})",
            "time_series_data": list_of_dicts,
            "analytics_stats": analytics_stats
        })

    @action(detail=False, methods=['get'], url_path='top-rated-games')
    def top_rated_games_report(self, request):
        min_reviews_str = request.query_params.get('min_reviews', '10')
        genre_name = request.query_params.get('genre')
        min_price_str = request.query_params.get('min_price')
        max_price_str = request.query_params.get('max_price')

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

        df = pd.DataFrame(list_of_dicts)
        analytics_stats = {}

        if not df.empty:
            df['avg_rating'] = pd.to_numeric(df['avg_rating'], errors='coerce')
            df['reviews_count'] = pd.to_numeric(df['reviews_count'], errors='coerce')
            df['price'] = pd.to_numeric(df['price'], errors='coerce')

            analytics_stats = {
                "total_games_in_report": df.shape[0],
                "mean_avg_rating": round(df['avg_rating'].mean(), 2),
                "max_avg_rating": round(df['avg_rating'].max(), 2),
                "min_avg_rating": round(df['avg_rating'].min(), 2),
                "median_avg_rating": round(df['avg_rating'].median(), 2),
                "total_reviews": int(df['reviews_count'].sum()),
                "mean_price": round(df['price'].mean(), 2)
            }

        report_title = f"Top Rated Games (Min Reviews: {min_reviews})"
        if genre_name:
            report_title += f" in Genre: {genre_name.title()}"

        return Response({
            "report_name": report_title,
            "time_series_data": list_of_dicts,
            "analytics_stats": analytics_stats
        })

    @action(detail=False, methods=['get'], url_path='whales-analysis')
    def whales_analysis(self, request):
        year = request.query_params.get('year')
        top_n_str = request.query_params.get('top_n', 10)
        user_ids_str = request.query_params.get('user_ids')

        try:
            top_n = int(top_n_str)
        except ValueError:
            top_n = 10

        spending_rank_qs = repo_manager.users.get_spending_rank(year=year)

        spending_rank_data = spending_rank_qs[:top_n]
        rank_serializer = UserSpendingRankSerializer(spending_rank_data, many=True)
        rank_list = rank_serializer.data

        if user_ids_str:
            selected_user_ids = [int(uid) for uid in user_ids_str.split(',') if uid.isdigit()]
        else:
            selected_user_ids = [user['id'] for user in rank_list]

        genre_breakdown_qs = repo_manager.users.get_whales_genre_breakdown(selected_user_ids)
        breakdown_serializer = WhalesGenreBreakdownSerializer(genre_breakdown_qs, many=True)
        genre_list = breakdown_serializer.data

        analytics_stats = {}
        if rank_list:
            df_rank = pd.DataFrame(rank_list)
            df_rank['total_spent'] = pd.to_numeric(df_rank['total_spent'], errors='coerce')

            analytics_stats = {
                "total_spending_top_n": round(df_rank['total_spent'].sum(), 2),
                "avg_spending_per_user": round(df_rank['total_spent'].mean(), 2),
                "total_orders_top_n": df_rank['orders_count'].sum(),
            }

        return Response({
            'report_name': f'Whales Analysis (Top {top_n} users, Year: {year or "All"})',
            'spending_rank': rank_list,
            'genre_breakdown': genre_list,
            'analytics_stats': analytics_stats
        })

    @action(detail=False, methods=['get'], url_path='user-activity')
    def user_activity_report(self, request):
        min_playtime_str = request.query_params.get('min_playtime', 0)
        top_n_str = request.query_params.get('top_n')

        report_data_qs = repo_manager.users.get_user_activity_report()

        serializer = UserActivityReportSerializer(report_data_qs, many=True)
        list_of_dicts = serializer.data

        df = pd.DataFrame(list_of_dicts)
        analytics_stats = {}
        correlation = None

        if not df.empty:
            df['total_playtime'] = pd.to_numeric(df['total_playtime'], errors='coerce')
            df['games_owned'] = pd.to_numeric(df['games_owned'], errors='coerce')

            try:
                min_playtime = int(min_playtime_str)
                df = df[df['total_playtime'] >= min_playtime]
            except ValueError:
                pass

            if not df.empty:
                correlation_matrix = df[['total_playtime', 'games_owned']].corr()
                correlation = round(correlation_matrix.loc['total_playtime', 'games_owned'], 4)

                analytics_stats = {
                    "total_active_users": df.shape[0],
                    "mean_playtime": round(df['total_playtime'].mean(), 2),
                    "median_games_owned": round(df['games_owned'].median(), 0),
                    "p75_playtime": round(df['total_playtime'].quantile(0.75), 2),
                    "playtime_games_correlation": correlation
                }

        if top_n_str:
            try:
                top_n = int(top_n_str)
                df_filtered = df.sort_values(by='total_playtime', ascending=False).head(top_n)
            except ValueError:
                df_filtered = df
        else:
            df_filtered = df

        return Response({
            "report_name": f"User Activity Report (Min Playtime: {min_playtime_str}h)",
            "activity_data": df_filtered.to_dict('records'),
            "analytics_stats": analytics_stats
        })
