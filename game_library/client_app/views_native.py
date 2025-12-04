from django.shortcuts import render, redirect
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal


from library_app.repositories.repository_manager import RepositoryManager
from .forms import GameForm

repo_manager = RepositoryManager()


@login_required
def native_list(request):
    games = repo_manager.games.get_all()

    developers = repo_manager.developers.get_all()
    publishers = repo_manager.publishers.get_all()
    genres = repo_manager.genres.get_all()

    search_query = request.GET.get('q')
    dev_filter = request.GET.get('developer')
    pub_filter = request.GET.get('publisher')
    genre_filter = request.GET.get('genre')

    if search_query:
        games = [g for g in games if search_query.lower() in g.title.lower()]

    if dev_filter:
        games = [g for g in games if str(g.developer_id) == dev_filter]

    if pub_filter:
        games = [g for g in games if str(g.publisher_id) == pub_filter]

    if genre_filter:
        games = [g for g in games if g.genre.filter(genre_id=genre_filter).exists()]

    user_data = repo_manager.users.get_by_id(request.user.pk)
    balance = user_data.balance if user_data else Decimal(0)

    context = {
        'games': games,
        'developers': developers,
        'publishers': publishers,
        'genres': genres,
        'balance': balance,
    }

    return render(request, 'client_app/game_list.html', context)


@login_required
def native_detail(request, pk):
    game = repo_manager.games.get_by_id(pk)

    if not game:
        raise Http404("Гру не знайдено")

    user_data = repo_manager.users.get_by_id(request.user.pk)
    balance = user_data.balance if user_data else Decimal(0)

    library = repo_manager.libraries.get_by_user(request.user.pk)
    is_owned = False
    if library:
        is_owned = repo_manager.library_games.is_game_in_library(library.pk, game.pk)

    return render(request, 'client_app/game_detail.html', {
        'game': game,
        'balance': balance,
        'is_owned': is_owned
    })


@login_required
def native_edit(request, pk=None):
    game = None
    if pk:
        game = repo_manager.games.get_by_id(pk)
        if not game:
            raise Http404("Гру не знайдено")

    form = GameForm(request.POST or None, instance=game)

    if request.method == 'POST':
        if form.is_valid():
            data = form.cleaned_data

            if pk:
                repo_manager.games.update(pk, **data)
            else:
                repo_manager.games.create(**data)

            return redirect('game_list')

    return render(request, 'client_app/game_form.html', {'form': form})


@login_required
def native_delete(request, pk):
    if request.method == 'POST':
        repo_manager.games.delete(pk)
        return redirect('game_list')

    return redirect('game_detail', pk=pk)


@login_required
def native_library(request):
    library = repo_manager.libraries.get_by_user(request.user.pk)

    if not library:
        library = repo_manager.libraries.create(user=request.user)

    my_games = library.games.all()

    user_data = repo_manager.users.get_by_id(request.user.pk)
    balance = user_data.balance if user_data else Decimal(0)

    return render(request, 'client_app/my_library.html', {
        'games': my_games,
        'library': library,
        'balance': balance
    })

@login_required
def add_balance(request):
    if request.method == 'POST':
        try:
            amount = Decimal(request.POST.get('amount', '0'))
        except:
            messages.error(request, "Некоректний формат суми")
            return redirect('game_list')

        if amount > 0:
            user = repo_manager.users.get_by_id(request.user.pk)
            if not user:
                messages.error(request, "Користувача не знайдено.")
                return redirect('game_list')

            new_balance = user.balance + amount
            repo_manager.users.update_balance(user.pk, new_balance)

            messages.success(request, f"Баланс поповнено на {amount} $!")
        else:
            messages.error(request, "Сума має бути більшою за нуль")

    return redirect('game_list')


@login_required
def buy_game(request, pk):
    game = repo_manager.games.get_by_id(pk)
    if not game:
        messages.error(request, "Гру не знайдено.")
        return redirect('game_list')

    user = repo_manager.users.get_by_id(request.user.pk)

    library = repo_manager.libraries.get_by_user(user)
    if library and repo_manager.library_games.is_game_in_library(library.pk, game.pk):
        messages.warning(request, "Ви вже маєте цю гру!")
        return redirect('game_list')

    if user.balance >= game.price:

        try:
            new_balance = user.balance - game.price
            repo_manager.users.update_balance(user.pk, new_balance)

            if not library:
                library = repo_manager.libraries.create(user=user)

            repo_manager.library_games.create(library=library, game=game)

            messages.success(request, f"Вітаємо! Ви купили {game.title}")
        except Exception as e:
            messages.error(request, f"Помилка купівлі: {e}")

    else:
        messages.error(request, "Недостатньо коштів на рахунку 😢")

    return redirect('game_list')


@login_required
def return_game(request, pk):
    if request.method == 'POST':
        game = repo_manager.games.get_by_id(pk)
        if not game:
            messages.error(request, "Гру не знайдено.")
            return redirect('library')

        user = repo_manager.users.get_by_id(request.user.pk)
        library = repo_manager.libraries.get_by_user(user)

        if not library:
            messages.error(request, "Бібліотеки не знайдено.")
            return redirect('library')


        lib_game_entry = repo_manager.library_games.model.objects.filter(library=library,
                                                                         game=game).first()

        if lib_game_entry:
            new_balance = user.balance + game.price
            repo_manager.users.update_balance(user.pk, new_balance)

            repo_manager.library_games.delete(lib_game_entry.pk)

            messages.success(request, f"Гру '{game.title}' успішно повернуто! {game.price} $ зараховано на баланс.")
        else:
            messages.error(request, "Цієї гри немає у вашій бібліотеці.")

    return redirect('library')