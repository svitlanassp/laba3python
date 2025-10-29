from library_app.models import LibraryGame, Library
from library_app.repositories.base_repository import BaseRepository


class LibraryGameRepository(BaseRepository):
    def __init__(self):
        super().__init__(LibraryGame)

    def get_all_by_library(self, library: Library):
        return self.model.objects.filter(library=library)
