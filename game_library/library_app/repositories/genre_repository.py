from django.db.models import Count

from library_app.models import Genre
from library_app.repositories.base_repository import BaseRepository


class GenreRepository(BaseRepository):
    def __init__(self):
        super().__init__(Genre)

    def get_genre_game_count_report(self):
        report_data = Genre.objects.annotate(
            game_count=Count('gamegenre_set')
        ).values('name', 'game_count')
        return list(report_data)