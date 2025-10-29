from library_app.models import Genre
from library_app.repositories.base_repository import BaseRepository


class GenreRepository(BaseRepository):
    def __init__(self):
        super().__init__(Genre)