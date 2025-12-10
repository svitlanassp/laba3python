from django.db.models import Count, Sum, F, FloatField, ExpressionWrapper, DecimalField, Q
from django.db.models.functions import Coalesce

from library_app.repositories.base_repository import BaseRepository
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(UserModel)

    def update_balance(self, user_id, new_balance):
        return self.update(user_id, balance=new_balance)

    def get_spending_rank(self, year=None):
        queryset = self.model.objects.all()

        year_filter = Q()
        if year:
            try:
                year = int(year)
                year_filter = Q(order__created_at__year=year)
            except ValueError:
                pass

        status_filter = Q(order__status='complete')

        combined_filter = status_filter & year_filter

        report_data = (
            queryset
            .annotate(
                total_spent=Coalesce(
                    Sum(
                        'order__total_amount',
                        filter=combined_filter
                    ),
                    0.0,
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                ),

                orders_count=Count(
                    'order',
                    filter=combined_filter,
                    distinct=True
                )
            )
            .values('id', 'username', 'total_spent', 'orders_count')
            .order_by('-total_spent')
            .exclude(total_spent__lte=0)
        )
        return report_data

    def get_whales_genre_breakdown(self, user_ids):
        if not user_ids:
            return []

        report_data = (
            self.model.objects
            .filter(
                id__in=user_ids,
                order__status='complete',
            )
            .values('order__ordergame__game__genre__name')
            .annotate(
                spent_on_genre=Coalesce(
                    Sum('order__ordergame__price_at_purchase'),
                    0.0,
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                ),
                genre_name=F('order__ordergame__game__genre__name')
            )
            .order_by('-spent_on_genre')
            .exclude(spent_on_genre__isnull=True)
            .exclude(genre_name__isnull=True)
        )
        return report_data

    def get_user_activity_report(self):
        report_data = (
            self.model.objects
            .annotate(
                games_owned=Count('library__librarygame__game_id', distinct=True),
                total_playtime=Sum('library__librarygame__playtime_hours')
            )
            .filter(games_owned__gt=0)
            .annotate(
                avg_playtime_per_game=ExpressionWrapper(
                    F('total_playtime') / F('games_owned'),
                    output_field=FloatField()
                )
            )
            .values('id', 'username', 'games_owned', 'total_playtime', 'avg_playtime_per_game')
            .order_by('-total_playtime', 'username')
        )
        return report_data