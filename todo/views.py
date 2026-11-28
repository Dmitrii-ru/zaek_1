from django.utils.safestring import mark_safe
from django.shortcuts import redirect, get_object_or_404, render
from django.views.generic import ListView
from todo.utils.user_session import UserSessionToDo, get_today, get_date, navigate_month, UserTodoDB
from .forms import AddTodo
from todo.utils.calendar_session_todo import MyCalendar
from django.contrib.auth.decorators import login_required

def get_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip







@login_required
def TodoSessionView(request, **kwargs):
    ust = UserTodoDB(request) # <-- используем новый класс
    # ... дальше код почти не меняется, но убираем передачу сессии в форму
    form_add_todo = AddTodo()
    if request.method == "POST":
        form_add_todo = AddTodo(request.POST)
        if form_add_todo.is_valid():
            # В форму больше не нужно передавать session_key
            ust.add_todo(request.POST['todo'], request.POST['add'])
            return redirect(request.path)
    today = get_today().isoformat()
    # Если нет дня то берем день сегодня
    day = ust.get_obj(kwargs.get('slug_day', today))
    # Берем текущий месяц и год
    day_datetime = get_date(day['slug'])
    cal = MyCalendar(day_datetime.year, day_datetime.month, ust)
    html_cal = cal.formatmonth(withyear=True)
    next_m = navigate_month(day_datetime)
    prev_m = navigate_month(day_datetime, prev=True)
    today_day = {'slug': today}
    context = {'cal': mark_safe(html_cal),
               'day': day,
               'form_add_todo': form_add_todo,
               'next_m': next_m,
               'prev_m': prev_m,
               'today_day': today_day,
               'style_btn1': 'btn btn-outline-dark',
               }

    return render(request, 'todo/todo_session.html', context)


def TodoDelReplaceSessionView(request, **kwargs):
    ust = UserSessionToDo(request)
    post_date = request.POST
    print(post_date)
    if request.method == 'POST':
        if request.POST.get('replace'):
            ust.replace_del(kwargs['slug_day'], post_date['replace'].split(','), rep=True)
        elif request.POST.get('del'):
            ust.replace_del(kwargs['slug_day'], post_date['del'].split(','))
    return redirect('todo_session_app:todo_session_day', kwargs['slug_day'])

