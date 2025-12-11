from django.db.models import Sum, Count, F, Q, DecimalField
from django.db.models.functions import Coalesce

from library_app.repositories.base_repository import BaseRepository
from library_app.models import Developer

class DeveloperRepository(BaseRepository):
    def __init__(self):
        super().__init__(Developer)

    def get_revenue_report(self, year=None):
        queryset = self.model.objects.all()

        filters = Q(game__ordergame__order__status='complete')
        if year:
            try:
                year = int(year)
                filters &= Q(game__ordergame__order__created_at__year=year)
            except ValueError:
                pass

        queryset = queryset.filter(filters).exclude(game__ordergame__id__isnull=True)

        report_data = (
            queryset
            .values('developer_id', 'name')
            .annotate(
                total_revenue=Coalesce(
                    Sum('game__ordergame__price_at_purchase'),
                    0.0,
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                ),

                total_copies_sold=Coalesce(Count('game__ordergame__id', distinct=True), 0),

                avg_price=Coalesce(
                    F('total_revenue') / F('total_copies_sold'),
                    0.0,
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                )
            )
            .order_by('-total_revenue')
            .filter(total_revenue__gt=0)
        )

        return report_data


