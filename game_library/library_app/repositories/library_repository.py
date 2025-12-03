from django.core.exceptions import ObjectDoesNotExist
from library_app.models import Library
from library_app.repositories.base_repository import BaseRepository
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class LibraryRepository(BaseRepository):
    def __init__(self):
        super().__init__(Library)

    def get_by_user(self, user):
        if isinstance(user, UserModel):
            user_pk = user.pk
        elif isinstance(user, int) or str(user).isdigit():
            user_pk = user
        else:
            return None

        try:
            return self.model.objects.get(user_id=user_pk)
        except ObjectDoesNotExist:
            return None