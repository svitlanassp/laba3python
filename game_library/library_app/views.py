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
    LibraryGameSerializer, OrderGameSerializer
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
        # Оскільки pk - це primary key (id), знаходимо користувача
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

                order_obj = repo_manager.orders.create(user=user, total_amount=game.price, status='Completed')
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

    @action(detail=False, methods=['get'])
    def count(self, request):
        report_data = self.repo.get_genre_game_count_report()
        return Response(report_data)


class GameGenreViewSet(BaseViewSet):
    repo = repo_manager.game_genres
    serializer_class = GameGenreSerializer
