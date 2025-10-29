from library_app.repositories.base_repository import BaseRepository
from library_app.models import Developer

class DeveloperRepository(BaseRepository):
    def __init__(self):
        super().__init__(Developer)