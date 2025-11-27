from django.shortcuts import render, redirect
from django.http import Http404
from .forms import GameForm
from library_app.repositories.game_repository import GameRepository

game_repository = GameRepository()


def native_list(request):
    # Використовуємо метод батьківського класу BaseRepository (припускаю, що там є get_all)
    games = game_repository.get_all()
    return render(request, 'client_app/game_list.html', {'games': games})


def native_detail(request, pk):
    # Отримуємо гру по ID через репозиторій
    game = game_repository.get_by_id(pk)

    if not game:
        raise Http404("Гру не знайдено")

    return render(request, 'client_app/game_detail.html', {'game': game})


def native_edit(request, pk=None):
    game = None
    if pk:
        # Якщо це редагування, спочатку шукаємо гру
        game = game_repository.get_by_id(pk)
        if not game:
            raise Http404("Гру не знайдено")

    # Передаємо instance=game, щоб форма заповнилась старими даними
    form = GameForm(request.POST or None, instance=game)

    if request.method == 'POST':
        if form.is_valid():
            # Отримуємо чисті дані (словник) з форми
            # Це важливо! Ми НЕ робимо form.save()
            data = form.cleaned_data

            if pk:
                # ОНОВЛЕННЯ: передаємо ID і словник аргументів
                # Твій репозиторій сам вийме 'genre' з **data і оновить зв'язки
                game_repository.update(pk, **data)
            else:
                # СТВОРЕННЯ: передаємо словник аргументів
                game_repository.create(**data)

            return redirect('native_list')

    return render(request, 'client_app/game_form.html', {'form': form})


def native_delete(request, pk):
    if request.method == 'POST':
        # ВИДАЛЕННЯ через репозиторій
        game_repository.delete(pk)
        return redirect('native_list')

    # Якщо випадково зайшли через GET, перекидаємо на деталі
    return redirect('native_detail', pk=pk)