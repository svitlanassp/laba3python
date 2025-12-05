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
    

