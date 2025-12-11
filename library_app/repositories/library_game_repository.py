from library_app.models import LibraryGame
from library_app.repositories.base_repository import BaseRepository
from django.db.models import Count

class LibraryGameRepository(BaseRepository):
    def __init__(self):
        super().__init__(LibraryGame)

    def get_owned_game_ids_by_user(self, user_id):
        owned_ids = LibraryGame.objects.filter(
            library__user_id=user_id
        ).values_list('game_id', flat=True)

        return set(owned_ids)

    def get_all_by_library_id(self, library_id):
        return self.model.objects.filter(library_id=library_id)

    def is_game_in_library(self, library_id, game_id):
        return self.model.objects.filter(
            library_id=library_id,
            game_id=game_id
        ).exists()
