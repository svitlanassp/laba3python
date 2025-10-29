from django.core.exceptions import ObjectDoesNotExist
from library_app.models import Library, User
from library_app.repositories.base_repository import BaseRepository


class LibraryRepository(BaseRepository):
    def __init__(self):
        super().__init__(Library)

    def get_by_user(self, user : User):
        try:
            return self.model.objects.get(user=user)
        except ObjectDoesNotExist:
            return None
