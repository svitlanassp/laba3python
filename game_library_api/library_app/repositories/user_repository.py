from django.db.models import Count, Sum, F, FloatField, ExpressionWrapper

from library_app.repositories.base_repository import BaseRepository
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(UserModel)

    def update_balance(self, user_id, new_balance):
        return self.update(user_id, balance=new_balance)

    def get_user_activity_report(self):
        report_data = (
            self.model.objects
            .annotate(
                games_owned=Count('library__librarygame__game_id',distinct=True),
                total_playtime=Sum('library__librarygame__playtime_hours')
            )
            .filter(games_owned__gt=0)
            .annotate(
                avg_playtime_per_game=ExpressionWrapper(
                    F('total_playtime') / F('games_owned'),
                    output_field=FloatField()
                )
            )
            .values('id','username','games_owned','total_playtime','avg_playtime_per_game')
            .order_by('-total_playtime','username')
        )
        return report_data

    def get_spending_rank(self,year=None):
        queryset = self.model.objects.filter(order__status='complete')

        if year:
            try:
                year = int(year)
                queryset = queryset.filter(order__created_at__year=year)
            except ValueError:
                pass

        report_data = (
            queryset
            .values('id','username')
            .annotate(
                total_spent=Sum('order__total_amount'),
                orders_count=Count('order')
            )
            .order_by('-total_spent')
            .exclude(total_spent__isnull=True)
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
            .values(
                'order__ordergame__game__genre__name'
            )
            .annotate(
                spent_on_genre=Sum('order__ordergame__price_at_purchase'),
                genre_name=F('order__ordergame__game__genre__name')
            )
            .order_by('-spent_on_genre')
            .exclude(order__games__genre__name__isnull=True)
        )
        return report_data