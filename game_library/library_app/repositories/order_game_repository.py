from library_app.models import OrderGame, Order
from library_app.repositories.base_repository import BaseRepository


class OrderGameRepository(BaseRepository):
    def __init__(self):
        super().__init__(OrderGame)

    def get_all_by_order(self, order : Order):
        return self.model.objects.filter(order=order)
