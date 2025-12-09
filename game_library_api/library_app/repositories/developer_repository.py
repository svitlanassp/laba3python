from django.db.models import Sum, Count, F

from library_app.repositories.base_repository import BaseRepository
from library_app.models import Developer

class DeveloperRepository(BaseRepository):
    def __init__(self):
        super().__init__(Developer)

    def get_revenue_report(self,year=None):
        queryset = self.model.objects.all()

        if year:
            try:
                year = int(year)
                queryset = queryset.filter(
                    game__ordergame__order__status='complete',
                    game__ordergame__order__created_at__year=year
                )
            except ValueError:
                pass
        else:
            queryset = queryset.filter(game__ordergame__order__status='complete')

        report_data = (
            queryset
            .values('developer_id','name')
            .annotate(
                total_revenue=Sum('game__ordergame__price_at_purchase'),
                total_copies_sold=Count('game__ordergame__id'),
                avg_price=F('total_revenue')/F('total_copies_sold')
            )
            .order_by('-total_revenue')
            .exclude(total_revenue__isnull=True)
        )
        return report_data