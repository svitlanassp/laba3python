from django.db.models import Count, Sum

from library_app.models import Genre
from library_app.repositories.base_repository import BaseRepository


class GenreRepository(BaseRepository):
    def __init__(self):
        super().__init__(Genre)

    def get_genre_game_count_report(self):
        report_data = Genre.objects.annotate(
            game_count=Count('gamegenre')
        ).values('name', 'game_count')
        return list(report_data)

    def get_top_genres_by_playtime(self,min_games_count=5):
        return(
            self.model.objects
            .values('name')
            .annotate(
                total_playtime=Sum('game__gamegenre__game__librarygame__playtime_hours'),
                game_count=Count('game__gamegenre__game',distinct=True)
            )
            .filter(game_count__gte=min_games_count)
            .order_by('-total_playtime','name')
        )