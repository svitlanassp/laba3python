from library_app.models import LibraryGame
from library_app.repositories.base_repository import BaseRepository


class LibraryGameRepository(BaseRepository):
    def __init__(self):
        super().__init__(LibraryGame)

    def get_all_by_library_id(self, library_id):
        return self.model.objects.filter(library_id=library_id)
