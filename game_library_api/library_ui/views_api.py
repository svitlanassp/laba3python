from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from requests.auth import HTTPBasicAuth

from .NetworkHelper import NetworkHelper

API_BASE_URL = 'http://127.0.0.1:8000/api/'
AUTH_USER = 'arisu'
AUTH_PASS = 'paowithbeijo'
AUTH = HTTPBasicAuth(AUTH_USER, AUTH_PASS)

network_helper = NetworkHelper(API_BASE_URL,AUTH)

@login_required
def game_list_view(request):
    user_id = request.user.pk

    all_games = network_helper.get_all_games()
    user_data = network_helper.get_user_data(user_id)

    if isinstance(all_games, dict) and 'error' in all_games:
        messages.error(request, 'Не вдалося завантажити список ігор із сервера API.')
        games_with_status = []
    else:
        games_with_status = all_games

    context = {
        'games': games_with_status,
        'balance': user_data.get('balance', 'N/A'),
        'username': request.user.username
    }
    return render(request, 'game_list.html', context)

@login_required
def game_detail_view(request, pk):
    game_data = network_helper.get_game_details(pk)
    user_data = network_helper.get_user_data(request.user.pk)

    if not game_data:
        messages.error(request, 'Гру не знайдено.')
        return redirect('game_list')

    is_owned = game_data.get('is_owned', False)

    context = {
        'game': game_data,
        'balance': user_data.get('balance', 'N/A'),
        'is_owned': is_owned,
    }
    return render(request, 'game_detail.html', context)


@login_required
def buy_game_view(request, pk):
    if request.method == 'POST':
        user_id = request.user.pk
        game_id = pk

        result = network_helper.buy_game(user_id, game_id)

        if result.get('error'):
            messages.error(request, result['error'])
        else:
            messages.success(request, f"{result['message']} Новий баланс: {result.get('new_balance', 'N/A')} $")

        return redirect('game_detail', pk=pk)

    return redirect('game_detail', pk=pk)


def user_logout(request):
    logout(request)
    return redirect('login')


@login_required
def top_up_balance_view(request):
    if request.method == 'POST':
        user_id = request.user.pk
        amount = request.POST.get('amount')

        try:
            amount = float(amount)
        except (TypeError, ValueError):
            messages.error(request, 'Некоректний формат суми.')
            return redirect('game_list')

        if amount <= 0:
            messages.error(request, 'Сума поповнення повинна бути позитивною.')
            return redirect('game_list')

        result = network_helper.top_up_balance(user_id, amount)

        if result.get('error'):
            messages.error(request, result['error'])
        else:
            messages.success(request, f"{result['message']} Новий баланс: {result.get('new_balance', 'N/A')} $")

        return redirect('game_list')



@login_required
def library_view(request):
    user_id = request.user.pk

    user_data = network_helper.get_user_data(user_id)
    balance = user_data.get('balance', 'N/A')

    library_games = network_helper.get_user_library(user_id)

    context = {
        'balance': balance,
        'games': library_games,
        'current_user': user_id,
        'view_title': 'Моя Бібліотека Ігор'
    }

    if isinstance(library_games, dict) and 'error' in library_games:
        messages.error(request, library_games['error'])
        context['games'] = []

    return render(request, 'library.html', context)