import requests
from requests.auth import HTTPBasicAuth

class NetworkHelper:
    def __init__(self, base_url, username, password):
        self.base_url = base_url.rstrip('/') + "/"
        self.auth = HTTPBasicAuth(username, password) if username and password else None

    def _get_url(self,endpoint, pk=None):
        url = self.base_url + endpoint.lstrip('/')
        if pk is not None:
            url += f"/{pk}/"
        return url

    def get(self, endpoint, pk=None):
        url = self._get_url(endpoint, pk)
        try:
            response = requests.get(url, auth=self.auth)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(e)
            return None

    def post(self, endpoint, data):
        url = self._get_url(endpoint)
        try:
            response = requests.post(url, json=data, auth=self.auth)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(e)
            return None

    def put(self, endpoint, pk, data):
        url = self._get_url(endpoint, pk)
        try:
            response = requests.put(url, json=data, auth=self.auth)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(e)
            return None

    def delete(self, endpoint, pk):
        url = self._get_url(endpoint, pk)
        try:
            response = requests.delete(url, auth=self.auth)
            response.raise_for_status()
            return response.status_code == 204
        except requests.exceptions.RequestException as e:
            print(e)
            return None

    # api games

    def get_games(self):
        return self.get('games') or []

    def get_game(self, pk):
        return self.get('games',pk)

    def create_game(self, data):
        return self.post('games',data)

    def update_game(self, pk, data):
        return self.put('games',pk,data)

    def delete_game(self, pk):
        return self.delete('games',pk)

    # api developers

    def get_developers(self):
        return self.get('developers') or []

    def get_developer(self, pk):
        return self.get('developers',pk)

    def create_developer(self, data):
        return self.post('developers',data)

    def update_developer(self, pk, data):
        return self.put('developers',pk,data)

    def delete_developer(self, pk):
        return self.delete('developers',pk)


