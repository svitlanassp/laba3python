from library_app.repositories.base_repository import BaseRepository
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(UserModel)

    def update_balance(self, user_id, new_balance):
        return self.update(user_id, balance=new_balance)