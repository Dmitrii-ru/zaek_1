from django import views
from django.urls import path
from . import views

app_name = 'todo_session_app'


urlpatterns = [
    path('', views.TodoSessionView, name='todo_session'),
    path('<slug_day>/', views.TodoSessionView, name='todo_session_day'),
    path('<slug_day>/del/', views.TodoDelReplaceSessionView, name='todo_session_del'),
    path('<slug_day>/remove/', views.TodoDelReplaceSessionView, name='todo_session_remove'),

]
