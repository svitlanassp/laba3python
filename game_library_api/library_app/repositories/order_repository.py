from datetime import datetime, timedelta

from django.db.models.functions import ExtractYear, ExtractMonth
from django.utils import timezone

from library_app.models import Order
from library_app.repositories.base_repository import BaseRepository
from django.db.models import Sum, Count

class OrderRepository(BaseRepository):
    def __init__(self):
        super().__init__(Order)

    def get_all_by_user_id(self, user_id):
        return self.model.objects.filter(user_id=user_id)

    def get_user_spending_report(self):
        return(
            self.model.objects
            .filter(status='complete')
            .values('user__username')
            .annotate(
                total_orders=Count('order_id'),
                total_spent=Sum('total_amount')
            )
            .order_by('-total_spent')
        )

    def get_monthly_revenue_report(self, start_date_str=None, end_date_str=None):
        queryset = self.model.objects.filter(status='complete')

        if start_date_str and end_date_str:
            try:
                naive_start = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                naive_end = datetime.strptime(end_date_str, '%Y-%m-%d').date()

                queryset = queryset.filter(
                    created_at__date__gte=naive_start,
                    created_at__date__lte=naive_end,
                )


            except ValueError:
                pass

        return(
            queryset
            .annotate(
                order_year = ExtractYear('created_at'),
                order_month = ExtractMonth('created_at')
            )
            .values('order_year', 'order_month')
            .annotate(
                total_revenue=Sum('total_amount')
            )
        )

