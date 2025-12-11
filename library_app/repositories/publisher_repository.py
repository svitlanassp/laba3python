from library_app.repositories.base_repository import BaseRepository
from library_app.models import Publisher

class PublisherRepository(BaseRepository):
    def __init__(self):
        super().__init__(Publisher)