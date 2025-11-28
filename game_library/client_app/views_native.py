from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from .forms import GameForm
from library_app.repositories.game_repository import GameRepository
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from library_app.models import Library, LibraryGame, Game, Developer, Publisher, Genre

game_repository = GameRepository()


@login_required
def native_list(request):
    # 1. Отримуємо всі ігри спочатку
    games = Game.objects.all()

    # 2. Отримуємо списки для випадайок (фільтрів)
    developers = Developer.objects.all()
    publishers = Publisher.objects.all()
    genres = Genre.objects.all()

    # 3. Отримуємо дані з URL (те, що вибрав користувач)
    search_query = request.GET.get('q')
    dev_filter = request.GET.get('developer')
    pub_filter = request.GET.get('publisher')
    genre_filter = request.GET.get('genre')

    # 4. ЗАСТОСОВУЄМО ФІЛЬТРИ (по черзі)

    # Пошук по назві
    if search_query:
        games = games.filter(title__icontains=search_query)

    # Фільтр по розробнику
    if dev_filter:
        games = games.filter(developer_id=dev_filter)

    # Фільтр по видавцю
    if pub_filter:
        games = games.filter(publisher_id=pub_filter)

    # Фільтр по жанру (через зв'язок Many-to-Many трохи інакше)
    if genre_filter:
        games = games.filter(genre__genre_id=genre_filter)

    # 5. Передаємо все це в шаблон
    context = {
        'games': games,
        'developers': developers,
        'publishers': publishers,
        'genres': genres,
    }

    return render(request, 'client_app/game_list.html', context)

@login_required
def native_detail(request, pk):
    game = game_repository.get_by_id(pk)

    if not game:
        raise Http404("Гру не знайдено")

    return render(request, 'client_app/game_detail.html', {'game': game})

@login_required
def native_edit(request, pk=None):
    game = None
    if pk:
        game = game_repository.get_by_id(pk)
        if not game:
            raise Http404("Гру не знайдено")

    form = GameForm(request.POST or None, instance=game)

    if request.method == 'POST':
        if form.is_valid():
            data = form.cleaned_data

            if pk:
                game_repository.update(pk, **data)
            else:
                game_repository.create(**data)

            return redirect('native_list')

    return render(request, 'client_app/game_form.html', {'form': form})

@login_required
def native_delete(request, pk):
    if request.method == 'POST':
        game_repository.delete(pk)
        return redirect('native_list')

    return redirect('native_detail', pk=pk)


@login_required
def native_library(request):
    library, created = Library.objects.get_or_create(user=request.user)

    my_games = library.games.all()

    return render(request, 'client_app/my_library.html', {'games': my_games, 'library': library})


@login_required
def add_balance(request):
    if request.method == 'POST':
        amount = float(request.POST.get('amount', 0))
        if amount > 0:
            library, _ = Library.objects.get_or_create(user=request.user)
            library.balance = float(library.balance) + amount
            library.save()
            messages.success(request, f"Баланс поповнено на {amount} грн!")
        else:
            messages.error(request, "Сума має бути більшою за нуль")

    return redirect('native_list')  # Повертаємось на головну


@login_required
def buy_game(request, pk):
    game = get_object_or_404(Game, pk=pk)
    library, _ = Library.objects.get_or_create(user=request.user)

    if library.games.filter(pk=pk).exists():
        messages.warning(request, "Ви вже маєте цю гру!")
        return redirect('native_list')

    if library.balance >= game.price:
        library.balance -= game.price
        library.save()

        LibraryGame.objects.create(library=library, game=game)

        messages.success(request, f"Вітаємо! Ви купили {game.title}")
    else:
        messages.error(request, "Недостатньо коштів на рахунку 😢")

    return redirect('native_list')

@login_required
def return_game(request, pk):
    if request.method == 'POST':
        game = get_object_or_404(Game, pk=pk)
        library = request.user.library

        lib_game_entry = LibraryGame.objects.filter(library=library, game=game).first()

        if lib_game_entry:
            library.balance += game.price
            library.save()

            lib_game_entry.delete()

            messages.success(request, f"Гру '{game.title}' успішно повернуто! {game.price} грн зараховано на баланс.")
        else:
            messages.error(request, "Цієї гри немає у вашій бібліотеці.")

    return redirect('native_library')