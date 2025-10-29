from library_app.models import Order
from library_app.repositories.base_repository import BaseRepository


class OrderRepository(BaseRepository):
    def __init__(self):
        super().__init__(Order)

    def get_all_by_user(self, user):
        return self.model.objects.filter(user=user)
    

