# pagination.py або в кінці views.py
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class StandardPagination(PageNumberPagination):
    page_size = 50  # Зміни з 10 на 50 для кращої продуктивності
    page_size_query_param = 'page_size'
    max_page_size = 1000

    def get_paginated_response(self, data):
        """Повертає пагіновану відповідь"""
        return Response({
            'count': self.page.paginator.count if hasattr(self, 'page') and self.page else len(data),
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })