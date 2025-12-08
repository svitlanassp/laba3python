from django.db.models import Avg, Count, F, ExpressionWrapper, FloatField

from library_app.models import Review
from library_app.repositories.base_repository import BaseRepository


class ReviewRepository(BaseRepository):
    def __init__(self):
        super().__init__(Review)

    def get_reviews_by_game(self,game_id):
        return self.model.objects.filter(game_id=game_id)

    def get_price_quality_ratio_report(self, min_review_count=10):
        return(
            self.model.objects
            .values('game__title','game__price')
            .annotate(
                avg_rating=Avg('rating'),
                reviews_count=Count('review_id'),
                price_quality_ratio=ExpressionWrapper(
                    F('game__price') / F('avg_rating'),
                    output_field=FloatField()
                )
            )
            .filter(reviews_count__gte=min_review_count)
            .order_by('-price_quality_ratio','-avg_rating')
        )