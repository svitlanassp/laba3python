from django.shortcuts import render, redirect
from .NetworkHelper import NetworkHelper

API_BASE_URL = 'http://127.0.0.1:8000/api/'
API_USER = 'arisu'
API_PASS = 'paowithbeijo'

api_client = NetworkHelper(API_BASE_URL, API_USER, API_PASS)

def api_list_games(request):
    games = api_client.get_games()
    return render(request, 'client_app/game_api_list.html', {'games': games})

def api_delete_game(request, pk):
    api_client.delete_game(pk)
    return redirect('api_list_games')

def api_list_developers(request):
    developers = api_client.get_developers()
    return render(request, 'client_app/developer_api_list.html', {'developers': developers})

def api_delete_developer(request, pk):
    api_client.delete_developer(pk)
    return redirect('api_list_developers')

