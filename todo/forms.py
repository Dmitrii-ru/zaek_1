from django import forms
from django.core.exceptions import ValidationError
from django.contrib.sessions.backends.db import SessionStore
from .utils.user_session import UserSessionToDo


class AddTodo(forms.Form):
    todo = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Новая задача'}), label='', required=False,
                           max_length=50)
    day_slug = forms.CharField(widget=forms.HiddenInput)
    sess = forms.CharField(widget=forms.HiddenInput)

    def clean(self):

        ust = UserSessionToDo(SessionStore(self.cleaned_data['sess']), sess=True)
        day = ust.todo_days[self.cleaned_data['day_slug']]
        todo = self.cleaned_data['todo']
        if not todo:
            raise ValidationError(
                f"Вы нечего не ввели")
        elif len(todo) > 50:
            raise ValidationError(
                "Не больше 20 символов")
        elif todo in day['actual']:
            raise ValidationError(
                f"Уже есть в Задачах на сегодня")
        elif todo in day['close']:
            raise ValidationError(
                f"Уже есть в Завершенных задачах")
        return todo
