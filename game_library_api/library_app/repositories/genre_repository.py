from django.db.models import Count, Sum, F, ExpressionWrapper, FloatField, OuterRef, Avg, Subquery

from library_app.models import Genre, Game
from library_app.repositories.base_repository import BaseRepository


class GenreRepository(BaseRepository):
    def __init__(self):
        super().__init__(Genre)

    def get_top_genres_by_playtime(self,min_games_count=5):
        annotated_queryset = (
            self.model.objects
            .values('name')
            .annotate(
                total_playtime=Sum('game__gamegenre__game__librarygame__playtime_hours'),

                total_copies=Count('game__gamegenre__game__librarygame__id'),

                unique_game_count=Count('game__gamegenre__game', distinct=True)
            )
        )

        filtered_queryset = annotated_queryset.filter(unique_game_count__gte=min_games_count)

        report_data = (
            filtered_queryset
            .annotate(
                avg_playtime_per_copy=ExpressionWrapper(
                    F('total_playtime') / F('total_copies'),
                    output_field=FloatField()
                )
            )
            .order_by('-avg_playtime_per_copy', 'name')
            .exclude(total_copies__isnull=True)
        )

        return report_data.values('name', 'avg_playtime_per_copy', 'unique_game_count')

