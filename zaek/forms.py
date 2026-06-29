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


class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label='CSV файл',
        help_text='Загрузите CSV файл с колонками: Название категории, Продукт, Вопрос, Ответ, Тема вопроса, Уровень сложности',
        widget=forms.FileInput(attrs={'accept': '.csv'})
    )