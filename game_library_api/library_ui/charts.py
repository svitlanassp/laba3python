import plotly.express as px
import pandas as pd

# 👇 ПРЯМИЙ ІМПОРТ (Це найнадійніший спосіб)
from library_app.repositories.genre_repository import GenreRepository


def build_playtime_chart(min_games):
    """
    Будує графік на основі реальних даних з БД.
    """
    # 1. Ініціалізуємо репозиторій
    repo = GenreRepository()

    # 2. Отримуємо дані (те саме, що ти вивела в консолі)
    # Перетворюємо QuerySet у список словників list(), щоб Pandas його з'їв
    data = list(repo.get_top_genres_by_playtime(min_games_count=min_games))

    # 3. Перевірка на порожнечу
    if not data:
        return "<div class='alert alert-warning'>Даних не знайдено для цього фільтру. Спробуйте зменшити кількість ігор.</div>"

    # 4. Створюємо DataFrame
    df = pd.DataFrame(data)

    # 5. Малюємо графік
    # Використовуємо твої реальні поля: 'avg_playtime_per_copy' та 'name'
    fig = px.bar(
        df,
        x='avg_playtime_per_copy',
        y='name',
        orientation='h',
        title=f'Топ жанрів за часом гри (мін. ігор: {min_games})',
        labels={
            'avg_playtime_per_copy': 'Середній час (год)',
            'name': 'Жанр'
        },
        color='avg_playtime_per_copy',
        template='plotly_white'
    )

    # Сортуємо (найбільші зверху)
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})

    return fig.to_html(full_html=False)