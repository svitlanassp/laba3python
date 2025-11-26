from django import forms
from library_app.models import Game


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        # Використовуємо поля з твоєї моделі models.py
        fields = ['title', 'description', 'price', 'release_date', 'developer', 'publisher', 'genre']

        # Додаємо календарик для дати і стилі для інших полів
        widgets = {
            'release_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'genre': forms.CheckboxSelectMultiple(),  # Або SelectMultiple, якщо хочеш список
        }
