from library_app.models import GameGenre
from library_app.repositories.base_repository import BaseRepository


class GameGenreRepository(BaseRepository):
    def __init__(self):
        super().__init__(GameGenre)

