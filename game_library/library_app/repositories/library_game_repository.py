from library_app.models import LibraryGame
from library_app.repositories.base_repository import BaseRepository
from django.db.models import Count

class LibraryGameRepository(BaseRepository):
    def __init__(self):
        super().__init__(LibraryGame)

    def get_all_by_library_id(self, library_id):
        return self.model.objects.filter(library_id=library_id)

    def get_game_popularity_report(self):
        return(
            self.model.objects
            .values('game__title')
            .annotate(
                library_count=Count('game_id')
            )
            .order_by('-library_count','game__title')
        )
