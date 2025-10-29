from library_app.models import Game
from library_app.repositories.base_repository import BaseRepository


class GameRepository(BaseRepository):
    def __init__(self):
        super().__init__(Game)
