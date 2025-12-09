from django.shortcuts import render
from .charts import build_playtime_chart


def playtime_dashboard_view(request):
    # 1. Отримуємо параметри фільтрації з URL
    # Якщо параметр не передано, використовуємо 5 за замовчуванням
    min_games_val = int(request.GET.get('min_unique_games', 5))

    # 2. Викликаємо нашу функцію малювання
    chart_html = build_playtime_chart(min_games_val)

    # 3. Передаємо дані в шаблон
    context = {
        'chart': chart_html,  # Готовий HTML графіка
        'current_min': min_games_val  # Щоб зберегти значення в полі вводу
    }

    return render(request, 'playtime_dashboard.html', context)