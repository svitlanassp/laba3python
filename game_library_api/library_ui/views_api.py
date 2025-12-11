from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from requests.auth import HTTPBasicAuth
from django.core.paginator import Paginator
import time
import pandas as pd
import plotly.express as px
from concurrent.futures import ThreadPoolExecutor
from django.db import connection

from .NetworkHelper import NetworkHelper

API_BASE_URL = 'http://127.0.0.1:8000/api/'
AUTH_USER = 'andriana'
AUTH_PASS = 'At14122005'
AUTH = HTTPBasicAuth(AUTH_USER, AUTH_PASS)

network_helper = NetworkHelper(API_BASE_URL,AUTH)

@login_required
def game_list_view(request):
    user_id = request.user.pk

    api_response = network_helper.get_all_games()
    user_data = network_helper.get_user_data(user_id)

    if isinstance(api_response, dict) and 'results' in api_response:
        games_list = api_response['results']
    elif isinstance(api_response, list):
        games_list = api_response
    else:
        games_list = []

    paginator = Paginator(games_list, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'games': page_obj,
        'balance': user_data.get('balance', 'N/A'),
        'username': request.user.username
    }
    return render(request, 'game_list.html', context)


@login_required
def game_detail_view(request, pk):
    user_id = request.user.pk

    game_data = network_helper.get_game_details(pk)
    user_data = network_helper.get_user_data(user_id)

    if not game_data:
        messages.error(request, 'Гру не знайдено.')
        return redirect('game_list')

    library_response = network_helper.get_user_library(user_id)

    is_owned = False

    if isinstance(library_response, list):
        for item in library_response:
            game_id_in_library = item.get('game')

            if str(game_id_in_library) == str(pk):
                is_owned = True
                break

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


def fetch_game_worker(game_id):
    try:
        network_helper.get_game_details(game_id)
    except Exception:
        pass
    finally:
        connection.close()


def parallel_db_test_view(request):
    all_games_response = network_helper.get_all_games()

    real_ids = []

    if isinstance(all_games_response, dict) and 'results' in all_games_response:
        real_ids = [game.get('id') or game.get('game_id') for game in all_games_response['results']]
    elif isinstance(all_games_response, list):
        real_ids = [game.get('id') or game.get('game_id') for game in all_games_response]

    if not real_ids:
        real_ids = [12, 101, 152, 158, 159]


    multiplier = (100 // len(real_ids)) + 1
    task_ids = (real_ids * multiplier)[:100]

    worker_counts = [1, 2, 4, 8, 16]
    results = []

    print(f"🚀 Починаємо тест на {len(task_ids)} запитах...")

    base_time = 0

    for workers in worker_counts:
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=workers) as executor:
            list(executor.map(fetch_game_worker, task_ids))

        end_time = time.time()
        duration = end_time - start_time

        if workers == 1:
            base_time = duration
            speedup = 1.0
        else:
            speedup = base_time / duration if duration > 0 else 0

        print(f"   --> {workers} потоків: {duration:.4f} сек (x{speedup:.2f})")

        results.append({
            'workers': workers,
            'time': round(duration, 4),
            'speedup': round(speedup, 2)
        })

    df = pd.DataFrame(results)
    fig = px.line(
        df,
        x='workers',
        y='time',
        markers=True, title='Залежність швидкості від кількості потоків',
        template='plotly_white'
    )
    chart_html = fig.to_html(full_html=False)

    context = {
        'chart': chart_html,
        'results_table': results,
        'total_requests': len(task_ids)
    }

    return render(request, 'parallel_db_test.html', context)