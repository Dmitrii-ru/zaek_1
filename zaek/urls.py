from django.urls import path
from .views import ZaekUserAPIView, RandomQuestionAPIView, UpdateStatsView

app_name = 'zaek_app'


urlpatterns = [
    path('api/zaek-user/', ZaekUserAPIView.as_view(), name='zaek-user-api'),
    path('api/zaek-question/', RandomQuestionAPIView.as_view(), name='zaek-question-api'),
    path('api/update_stats/', UpdateStatsView.as_view(), name='zaek-update_stats-api'),
]


