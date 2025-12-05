from library_app.models import Game, GameGenre, LibraryGame
from library_app.repositories.base_repository import BaseRepository


class GameRepository(BaseRepository):
    def __init__(self):
        super().__init__(Game)

    def create(self, **kwargs):
        genres = kwargs.pop('genre', [])

        game_obj = super().create(**kwargs)

        if genres:
            for genre_item in genres:
                GameGenre.objects.create(game=game_obj, genre=genre_item)

        return game_obj

    def update(self, pk, **kwargs):
        genres = kwargs.pop('genre', None)

        game_obj = super().update(pk, **kwargs)

        if genres is not None:
            GameGenre.objects.filter(game=game_obj).delete()
            for genre_item in genres:
                GameGenre.objects.create(game=game_obj, genre=genre_item)

        return game_obj

    def check_if_user_owns_game(self, user_id: int, game_id: int) -> bool:
        try:
            return LibraryGame.objects.filter(
                library__user_id=user_id,
                game_id=game_id
            ).exists()
        except Exception as e:
            print(f"Помилка при перевірці володіння: {e}")
            return False
