from decimal import Decimal

from django.db import transaction
from django.utils import timezone
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
    LibraryGameSerializer, OrderGameSerializer, ReviewSerializer, PriceQualityReportSerializer,
    GenrePlaytimeReportSerializer, MonthlyRevenueReportSerializer
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

    @action(detail=False, methods=['get'])
    def report(self,request):
        report_data = self.repo.get_user_spending_report()
        return Response(list(report_data))

    @action(detail=False, methods=['get'], url_path='monthly-revenue')
    def monthly_revenue_report(self,request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        report_data = self.repo.get_monthly_revenue_report(start_date_str=start_date,end_date_str=end_date)

        serializer = MonthlyRevenueReportSerializer(report_data,many=True)
        return Response(serializer.data)


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

    @action(detail=False, methods=['get'])
    def report(self, request):
        report_data = self.repo.get_game_popularity_report()
        return Response(list(report_data))

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

    @action(detail=False, methods=['get'], url_path='playtime-ranking')
    def playtime_ranking(self, request):
        min_games = request.query_params.get('min_games',5)
        report_data = self.repo.get_top_genres_by_playtime(min_games_count=int(min_games))
        serializer = GenrePlaytimeReportSerializer(report_data,many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def count(self, request):
        report_data = self.repo.get_genre_game_count_report()
        return Response(report_data)


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

    @action(detail=False, methods=['get'], url_path='price-quality-ratio')
    def price_quality_report(self,request):
        sort_order = request.query_params.get('sort','worst')
        report_data = self.repo.get_price_quality_ratio_report()

        if sort_order == 'best':
            report_data = report_data.order_by('price_quality_ratio', '-avg_rating')

        serializer = PriceQualityReportSerializer(report_data, many=True)
        return Response(serializer.data)