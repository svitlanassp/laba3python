from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import UserSerializer, LibrarySerializer, OrderSerializer, LibraryGameSerializer, OrderGameSerializer
from library_app.repositories.repository_manager import RepositoryManager
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated

repo_manager = RepositoryManager()

class BaseViewSet(viewsets.ViewSet):
    repository = None
    serializer_class = None
    write_serializer_class = None
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

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

class UserViewSet(BaseViewSet):
    repository = repo_manager.users
    serializer_class = UserSerializer

class OrderViewSet(BaseViewSet):
    repository = repo_manager.orders
    serializer_class = OrderSerializer

    @action(detail=False, methods=['get'])
    def spending_report(self,request):
        report_data = self.repository.get_user_spending_report()
        return Response(list(report_data))


class LibraryViewSet(BaseViewSet):
    repository = repo_manager.libraries
    serializer_class = LibrarySerializer

class LibraryGameViewSet(BaseViewSet):
    repository = repo_manager.library_games
    serializer_class = LibraryGameSerializer

    @action(detail=False, methods=['get'])
    def popularity_report(self, request):
        report_data = self.repository.get_game_popularity_report()
        return Response(list(report_data))

class OrderGameViewSet(BaseViewSet):
    repository = repo_manager.order_games
    serializer_class = OrderGameSerializer

