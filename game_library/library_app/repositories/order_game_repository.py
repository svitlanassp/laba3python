from library_app.models import OrderGame
from library_app.repositories.base_repository import BaseRepository


class OrderGameRepository(BaseRepository):
    def __init__(self):
        super().__init__(OrderGame)

    def get_all_by_order_id(self, order_id):
        return self.model.objects.filter(order_id=order_id)
