from django import views
from django.urls import path


from .views import (ZaekUserAPIView,
                    RandomQuestionAPIView,
                    UpdateStatsView,
                    CSVUploadView,
                    index, category_detail, user_profile, get_question_ajax, check_answer_ajax, reset_category,
                    zaek_user_api, random_question_api, update_stats_api, upload_csv, test_func)
from .utils.decoded import decoder_func
app_name = 'zaek_app'


# urlpatterns = [
#     path('', index, name='index'),
#     path('category/<int:category_id>/', category_detail, name='category_detail'),
#     path('profile/', user_profile, name='profile'),
#     path('get-question/', get_question_ajax, name='get_question_ajax'),
#     path('check-answer/', check_answer_ajax, name='check_answer_ajax'),
#     path('reset-category/<int:category_id>/', reset_category, name='reset_category'),
#     path('api/zaek-user/', ZaekUserAPIView.as_view(), name='zaek-user-api'),
#     path('api/zaek-question/', RandomQuestionAPIView.as_view(), name='zaek-question-api'),
#     path('api/update_stats/', UpdateStatsView.as_view(), name='zaek-update_stats-api'),
#     path('decoded/',decoder_func, name='zaek-decoded'),
#     path('upload-csv/', CSVUploadView.as_view(), name='upload-csv'),
#     # path('q', test_func, name='zaek-question'),
#
# ]
urlpatterns = [
path('', index, name='index'),
path('category/<int:category_id>/', category_detail, name='category_detail'),
path('profile/', user_profile, name='profile'),

# AJAX эндпоинты
path('get-question/', get_question_ajax, name='get_question_ajax'),
path('check-answer/', check_answer_ajax, name='check_answer_ajax'),
path('reset-category/<int:category_id>/', reset_category, name='reset_category'),

# API эндпоинты
path('api/zaek-user/', zaek_user_api, name='zaek-user-api'),
path('api/zaek-question/', random_question_api, name='zaek-question-api'),
path('api/update_stats/', update_stats_api, name='zaek-update_stats-api'),

# Дополнительные страницы
path('decoded/', decoder_func, name='zaek-decoded'),
path('upload-csv/', upload_csv, name='upload-csv'),
path('api/qa/', test_func, name='zaek-question'),
]