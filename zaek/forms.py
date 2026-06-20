from django import forms

class QuizForm(forms.Form):
    pres_info = forms.CharField(
        label='Введите данные викторины (presInfo)',
        widget=forms.Textarea(attrs={
            'rows': 10,
            'cols': 80,
            'placeholder': 'Вставьте сюда закодированную строку presInfo...'
        }),
        required=True
    )