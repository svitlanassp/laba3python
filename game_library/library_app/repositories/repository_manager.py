from .user_repository import UserRepository
from .game_repository import GameRepository
from .library_repository import LibraryRepository
from .library_game_repository import LibraryGameRepository
from .order_repository import OrderRepository
from .order_game_repository import OrderGameRepository
from .developer_repository import DeveloperRepository
from .publisher_repository import PublisherRepository
from .genre_repository import GenreRepository

class RepositoryManager:
    def __init__(self):
        self.users = UserRepository()
        self.games = GameRepository()
        self.libraries = LibraryRepository()
        self.library_games = LibraryGameRepository()
        self.orders = OrderRepository()
        self.order_games = OrderGameRepository()
        self.developers = DeveloperRepository()
        self.publishers = PublisherRepository()
        self.genres = GenreRepository()