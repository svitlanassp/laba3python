from django.core.exceptions import ObjectDoesNotExist

class BaseRepository:
    def __init__(self, model):
        self.model = model

    def get_all(self):
        return self.model.objects.all()

    def get_by_id(self, pk):
        try:
            return self.model.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return None

    def create(self, **kwargs):
        try:
            return self.model.objects.create(**kwargs)
        except Exception as e:
            print("Error creating object:", e)
            return None



