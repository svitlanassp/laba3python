from django import forms
from library_app.models import Game


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['title', 'description', 'price', 'release_date', 'developer', 'publisher', 'genre']

        widgets = {
            'release_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'genre': forms.CheckboxSelectMultiple(),
            'price': forms.NumberInput(attrs={'min': '0', 'step': '0.1'}),
        }