from django.shortcuts import render, redirect
from django.http import Http404
from .forms import GameForm
from library_app.repositories.game_repository import GameRepository

game_repository = GameRepository()


def native_list(request):
    games = game_repository.get_all()
    return render(request, 'client_app/game_list.html', {'games': games})


def native_detail(request, pk):
    game = game_repository.get_by_id(pk)

    if not game:
        raise Http404("Гру не знайдено")

    return render(request, 'client_app/game_detail.html', {'game': game})


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


def native_delete(request, pk):
    if request.method == 'POST':
        game_repository.delete(pk)
        return redirect('native_list')

    return redirect('native_detail', pk=pk)
