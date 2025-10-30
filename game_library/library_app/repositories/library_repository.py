from django.core.exceptions import ObjectDoesNotExist
from library_app.models import Library
from library_app.repositories.base_repository import BaseRepository


class LibraryRepository(BaseRepository):
    def __init__(self):
        super().__init__(Library)

    def get_by_user_id(self, user_id):
        try:
            return self.model.objects.get(user_id=user_id)
        except ObjectDoesNotExist:
            return None
