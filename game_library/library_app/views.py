from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from library_app.repositories.repository_manager import RepositoryManager
from .serializers import (
    GameSerializer, GameWriteSerializer, DeveloperSerializer,
    PublisherSerializer, GenreSerializer, GameGenreSerializer
)

repo_manager = RepositoryManager()

class BaseViewSet(viewsets.ViewSet):
    repository = None
    serializer_class = None
    write_serializer_class = None

    def list(self, request):
        queryset = self.repository.get_all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        write_serializer = self.write_serializer_class or self.serializer_class
        serializer = write_serializer(data=request.data)

        if serializer.is_valid():
            new_obj = self.repository.create(**serializer.validated_data)
            read_serializer = self.serializer_class(new_obj)
            return Response(read_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        obj = self.repository.get_by_id(pk)
        if obj:
            serializer = self.serializer_class(obj)
            return Response(serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        write_serializer = self.write_serializer_class or self.serializer_class
        serializer = write_serializer(data=request.data)

        if serializer.is_valid():
            updated_obj = self.repository.update(pk, **serializer.validated_data)
            if updated_obj:
                read_serializer = self.serializer_class(updated_obj)
                return Response(read_serializer.data)
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        deleted = self.repository.delete(pk)
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)


class GameViewSet(BaseViewSet):
    repository = repo_manager.games
    serializer_class = GameSerializer
    write_serializer_class = GameWriteSerializer # Окремий для POST/PUT


class DeveloperViewSet(BaseViewSet):
    repository = repo_manager.developers
    serializer_class = DeveloperSerializer
    write_serializer_class = DeveloperSerializer


class PublisherViewSet(BaseViewSet):
    repository = repo_manager.publishers
    serializer_class = PublisherSerializer
    write_serializer_class = PublisherSerializer


class GenreViewSet(BaseViewSet):
    repository = repo_manager.genres
    serializer_class = GenreSerializer
    write_serializer_class = GenreSerializer

    @action(detail=False, methods=['get'])
    def report_game_count(self, request):
        report_data = self.repository.get_genre_game_count_report()
        return Response(report_data)


class GameGenreViewSet(BaseViewSet):
    repository = repo_manager.game_genres
    serializer_class = GameGenreSerializer
    write_serializer_class = GameGenreSerializer

