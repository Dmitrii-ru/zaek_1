from datetime import datetime, timedelta, date
from calendar import HTMLCalendar
from django.urls import reverse


class MyCalendar(HTMLCalendar):
    def __init__(self, year=None, month=None, ust=None):
        self.year = year
        self.month = month
        self.ust = ust
        super(MyCalendar, self).__init__()

    def formatday(self, day, **kwargs):
        d = ''
        if day != 0:
            day_d = date(self.year, self.month, day).isoformat()
            url = reverse('todo_session_app:todo_session_day', args=(day_d,))

            dd = self.ust.todo_days.get(day_d, None)
            if dd and dd['actual']:
                return f"<td><a  class = 'a_todo_ses' href = '{url}'><div class = 'date_act'> <span class='date'>{day}</span></div></a></td>"
            else:
                return f"<td><a  class = 'a_todo_ses' href = '{url}'><div class = 'date_a'> <span class='date'>{day}</span></div></a></td>"
        return '<td></td>'

    def formatweek(self, theweek):
        week = ''
        for d, weekday in theweek:
            week += self.formatday(d)
        return f'<tr> {week} </tr>'

    def formatmonth(self, withyear=True, **kwargs):

        cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear).title()}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week, )}\n'
        cal += '</table>'
        return cal