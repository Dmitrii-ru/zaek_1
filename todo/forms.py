from django import forms
from django.core.exceptions import ValidationError
from django.contrib.sessions.backends.db import SessionStore
from .utils.user_session import UserSessionToDo


# class AddTodo(forms.Form):
#     todo = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Новая задача'}), label='', required=False,
#                            max_length=50)
#     day_slug = forms.CharField(widget=forms.HiddenInput)
#     sess = forms.CharField(widget=forms.HiddenInput)
#
#     def clean(self):
#
#         ust = UserSessionToDo(SessionStore(self.cleaned_data['sess']), sess=True)
#         day = ust.todo_days[self.cleaned_data['day_slug']]
#         todo = self.cleaned_data['todo']
#         if not todo:
#             raise ValidationError(
#                 f"Вы нечего не ввели")
#         elif len(todo) > 50:
#             raise ValidationError(
#                 "Не больше 20 символов")
#         elif todo in day['actual']:
#             raise ValidationError(
#                 f"Уже есть в Задачах на сегодня")
#         elif todo in day['close']:
#             raise ValidationError(
#                 f"Уже есть в Завершенных задачах")
#         return todo


class AddTodo(forms.Form):
    todo = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Новая задача'}), label='', required=False, max_length=50)
    day_slug = forms.CharField(widget=forms.HiddenInput, required=False)

    def clean(self):
        cleaned_data = super().clean()
        todo = cleaned_data.get('todo')
        if not todo:
            raise ValidationError("Введите задачу")
        if len(todo) > 50:
            raise ValidationError("Не более 50 символов")
        # Проверку на дубликаты лучше делать во вьюхе, так как для этого нужен self.user,
        # которого в форме нет, либо передавать user в форму.
        return cleaned_data