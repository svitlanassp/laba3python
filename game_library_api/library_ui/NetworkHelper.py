import requests
from requests.auth import HTTPBasicAuth


class NetworkHelper:
    def __init__(self, base_url, auth):
        self.API_BASE_URL = base_url
        self.AUTH = auth

    def get_all_games(self, page=None, page_size=None):
        try:
            params = {}
            if page is not None:
                params['page'] = page
            if page_size is not None:
                params['page_size'] = page_size

            response = requests.get(
                self.API_BASE_URL + 'games/',
                auth=self.AUTH,
                params=params
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Помилка отримання ігор: {e}")
            return []

    def get_game_details(self, game_id):
        try:
            response = requests.get(
                f"{self.API_BASE_URL}games/{game_id}/",
                auth=self.AUTH
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None

    def get_user_data(self, user_id):
        try:
            response = requests.get(f"{self.API_BASE_URL}users/{user_id}/data/", auth=self.AUTH)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return {"error": "Не вдалося отримати дані користувача"}

    def buy_game(self, user_id, game_id):
        payload = {
            "user_id": user_id,
            "game_id": game_id
        }
        try:
            response = requests.post(
                self.API_BASE_URL + 'games/buy/',
                json=payload,
                auth=self.AUTH
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.content:
                return {"error": e.response.json().get('error', 'Помилка API при купівлі')}
            return {"error": "Помилка HTTP"}
        except requests.exceptions.RequestException:
            return {"error": "Збій зв'язку з API-сервером."}

    def top_up_balance(self, user_id, amount):
        payload = {"amount": amount}
        url = f"{self.API_BASE_URL}users/{user_id}/top_up/"

        try:
            response = requests.post(url, json=payload, auth=self.AUTH)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.content:
                return {"error": e.response.json().get('error', 'Помилка API при поповненні')}
            return {"error": "Помилка HTTP"}
        except requests.exceptions.RequestException:
            return {"error": "Збій зв'язку з API-сервером."}

    def get_user_library(self, user_id):
        url = f"{self.API_BASE_URL}libraries/?user={user_id}"

        try:
            response = requests.get(url, auth=self.AUTH)
            response.raise_for_status()
            library_data = response.json()

            if library_data and library_data[0].get('library_games'):
                return library_data[0]['library_games']

            return []

        except requests.exceptions.RequestException:
            return {"error": "Збій зв'язку з API-сервером під час отримання бібліотеки."}

    def check_if_owned_by_api(self, user_id, game_id):
        url = f"{self.API_BASE_URL}games/{game_id}/is_owned/"

        params = {'user_id': user_id}

        try:
            response = requests.get(url, params=params, auth=self.AUTH)
            response.raise_for_status()

            return response.json().get('is_owned', False)

        except requests.exceptions.RequestException:
            return False