from django.db.models import Avg, Count, F, ExpressionWrapper, FloatField

from library_app.models import Review
from library_app.repositories.base_repository import BaseRepository


class ReviewRepository(BaseRepository):
    def __init__(self):
        super().__init__(Review)

    def get_reviews_by_game(self,game_id):
        return self.model.objects.filter(game_id=game_id)
