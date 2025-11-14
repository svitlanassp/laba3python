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

class OrderViewSet(BaseViewSet):
    repo = repo_manager.orders
    serializer_class = OrderSerializer

    @action(detail=False, methods=['get'])
    def spending_report(self,request):
        report_data = self.repo.get_user_spending_report()
        return Response(list(report_data))


class LibraryViewSet(BaseViewSet):
    repo = repo_manager.libraries
    serializer_class = LibrarySerializer

class LibraryGameViewSet(BaseViewSet):
    repo = repo_manager.library_games
    serializer_class = LibraryGameSerializer

    @action(detail=False, methods=['get'])
    def popularity_report(self, request):
        report_data = self.repo.get_game_popularity_report()
        return Response(list(report_data))

class OrderGameViewSet(BaseViewSet):
    repo = repo_manager.order_games
    serializer_class = OrderGameSerializer

class GameViewSet(BaseViewSet):
    repo = repo_manager.games
    serializer_class = GameSerializer


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
    def report_game_count(self, request):
        report_data = self.repo.get_genre_game_count_report()
        return Response(report_data)


class GameGenreViewSet(BaseViewSet):
    repo = repo_manager.game_genres
    serializer_class = GameGenreSerializer
