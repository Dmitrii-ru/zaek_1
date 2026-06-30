from django.http import HttpResponse
from django.shortcuts import render

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# from .fanc import get_random_question_data
from zaek.models import ZaekUser, ZaekQuestion, ZaekAnswer
from .serializers import ZaekUserSerializer
import random


class ZaekUserAPIView(APIView):
    def post(self, request):
        id_telegram = request.data.get('id_telegram')
        name_telegram = request.data.get('name_telegram')
        if not id_telegram:
            return Response({"error": "id_telegram is required"}, status=status.HTTP_400_BAD_REQUEST)

        user, created = ZaekUser.objects.get_or_create(
            id_telegram=id_telegram,
            defaults={
                'total_attempts': 0,
                'correct_attempts': 0,
                'show': True,
                'name_telegram' : name_telegram
            }
        )

        serializer = ZaekUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RandomQuestionAPIView(APIView):
    def get(self, request):
        questions = ZaekQuestion.objects.all()
        if not questions.exists():
            return Response({"error": "No questions available"}, status=404)

        random_question = random.choice(questions)
        answers = ZaekAnswer.objects.filter(question=random_question)

        question_data = {
            "product": random_question.product.name if random_question.product else None,
            "question": random_question.name,
            "comment": random_question.comment,
            "answers": [
                {
                    "text": answer.text,
                    "is_correct": answer.is_correct
                }
                for answer in answers
            ]
        }
        return Response(question_data)


class UpdateStatsView(APIView):
    def post(self, request):
        telegram_id = request.data.get('telegram_id')
        is_correct = request.data.get('is_correct')

        if not telegram_id:
            return Response(
                {"error": "telegram_id and is_correct are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = ZaekUser.objects.get(id_telegram=telegram_id)
            user.total_attempts += 1
            if is_correct:
                user.correct_attempts += 1
            user.save()
            print(user.correct_attempts,user.total_attempts)
            return Response({"status": "success"})
        except ZaekUser.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )


# async def test_func(request):
#     await get_random_question_data()
#     return HttpResponse("Hello, World!")
from django.shortcuts import render
from django.views import View
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.contrib import messages

from .forms import CSVUploadForm
from .utils.csv_loader import CSVLoader


@method_decorator(staff_member_required, name='dispatch')
class CSVUploadView(View):

    """View для загрузки CSV файла с вопросами"""

    def get(self, request):
        form = CSVUploadForm()
        return render(request, 'zaek_app/upload_csv.html', {'form': form})

    def post(self, request):
        print('CSVUploadView(View)')
        form = CSVUploadForm(request.POST, request.FILES)

        if not form.is_valid():
            print('if not form.is_valid()')
            return render(request, 'zaek_app/upload_csv.html', {'form': form})

        csv_file = form.cleaned_data['csv_file']

        # Загружаем данные
        loader = CSVLoader(csv_file)
        result = loader.load()

        # Добавляем сообщение об успехе/ошибке
        if result['errors']:
            messages.error(request, f'Загрузка завершена с ошибками. Пропущено: {result["skipped"]}')
        else:
            messages.success(request,
                             f'Успешно загружено! Создано: {result["created"]}, Обновлено: {result["updated"]}')

        return render(request, 'zaek_app/upload_csv.html', {
            'form': form,
            'result': result,
        })

#############################################################################################################################################################
# zaek/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Q, F
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import random
from .models import ZaekTopic, ZaekQuestion, TopicCategory, DifficultyLevel, ZaekAnswer, ZaekProduct
from core.redis import user_stats_service


# ==================== ВЕБ-СТРАНИЦЫ ====================

@login_required
def index(request):
    """Главная страница с категориями"""
    categories = TopicCategory.objects.annotate(
        question_count=Count('products__questions')
    ).filter(question_count__gt=0)

    context = {
        'categories': categories,
        'total_questions': ZaekQuestion.objects.count(),
    }
    return render(request, 'zaek_app/index.html', context)


@login_required
def category_detail(request, category_id):
    """Страница с вопросами по категории"""
    category = get_object_or_404(TopicCategory, id=category_id)

    context = {
        'category': category,
    }
    return render(request, 'zaek_app/category_detail.html', context)


@login_required
def user_profile(request):
    """Страница профиля пользователя"""
    context = {
        'username': request.user.username,
        'total_attempts': 0,
        'correct_attempts': 0,
    }
    return render(request, 'zaek_app/profile.html', context)


# ==================== AJAX ЭНДПОИНТЫ ====================

@csrf_exempt
@require_POST
def get_question_ajax(request):
    """AJAX запрос для получения следующего вопроса"""
    try:
        data = json.loads(request.body)
        category_id = data.get('category_id')
        telegram_id = str(request.user.id)

        # Получаем данные из Redis
        answered_questions = user_stats_service.get_answered_questions(telegram_id)
        blocked_questions = user_stats_service.get_blocked_questions(telegram_id)

        answered_ids = {int(qid) for qid in answered_questions if str(qid).isdigit()}
        blocked_ids = {int(qid) for qid in blocked_questions if str(qid).isdigit()}

        # Исключаем отвеченные и заблокированные вопросы
        excluded_ids = answered_ids.union(blocked_ids)

        category_none = True
        reset_occurred = False
        all_questions_answered = False

        # Проверяем category_id
        if not str(category_id).isdigit():
            question = random.choice(ZaekQuestion.objects.all())
            category_id = question.product.category.id
            category_none = None

        # Получаем вопросы по категории, исключая отвеченные и заблокированные
        questions = ZaekQuestion.objects.filter(
            product__category_id=category_id
        ).exclude(
            id__in=excluded_ids
        ).annotate(
            difficulty_level=F('difficulty__level')
        ).order_by('difficulty_level')

        min_difficulty_level = None

        if questions.exists():
            first_question = questions.first()
            min_difficulty_level = first_question.difficulty_level
            questions = [obj for obj in questions if obj.difficulty_level == min_difficulty_level]
        else:
            questions = []

        # Если вопросов нет, проверяем все ли отвечены
        if not questions:
            category_question_ids = ZaekQuestion.objects.filter(
                product__category_id=category_id
            ).values_list('id', flat=True)

            if excluded_ids.issuperset(set(category_question_ids)):
                all_questions_answered = True
                return JsonResponse({
                    'completed': True,
                    'message': 'Поздравляем! Вы ответили на все вопросы в этой категории!',
                    'category_name': TopicCategory.objects.get(id=category_id).name,
                })
            else:
                # Сбрасываем только отвеченные вопросы (не заблокированные)
                only_answered_ids = answered_ids - blocked_ids
                user_stats_service.remove_category_questions(telegram_id, list(only_answered_ids))

                questions = list(ZaekQuestion.objects.filter(product__category_id=category_id))
                reset_occurred = True

                if questions:
                    questions_with_difficulty = ZaekQuestion.objects.filter(
                        product__category_id=category_id
                    ).annotate(
                        difficulty_level=F('difficulty__level')
                    ).order_by('difficulty_level')

                    if questions_with_difficulty.exists():
                        min_difficulty_level = questions_with_difficulty.first().difficulty_level
                        questions = [obj for obj in questions_with_difficulty if
                                     obj.difficulty_level == min_difficulty_level]

        if not questions:
            return JsonResponse({'error': 'Нет доступных вопросов'}, status=404)

        # С вероятностью 99% показываем обычный вопрос, 1% - вопрос с изображением
        number = random.randint(1, 100)

        if number < 100:  # Обычный вопрос
            question = random.choice(questions)
            answers = list(ZaekAnswer.objects.filter(question=question))
            topic = question.topic

            # Убираем дубликаты ответов
            unique_answers = {}
            for a in answers:
                if a.text not in unique_answers:
                    unique_answers[a.text] = a

            # Если меньше 4 ответов, добираем из других вопросов той же темы
            if len(unique_answers) < 4:
                additional_answers = ZaekAnswer.objects.filter(
                    question__topic=topic
                ).exclude(question=question)

                for a in additional_answers:
                    if a.text not in unique_answers and len(unique_answers) < 4:
                        # Делаем дополнительные ответы неправильными
                        a.is_correct = False
                        unique_answers[a.text] = a

            answers = list(unique_answers.values())
            random.shuffle(answers)

            # ============ ЛОГИКА ИЗОБРАЖЕНИЙ ============
            # Приоритет: 1. URL из вопроса, 2. Изображение продукта, 3. URL продукта
            image_data = None

            # Проверяем есть ли URL изображения у вопроса
            if question.image_url and question.image_url.strip():
                image_data = {
                    "type": "url",
                    "url": question.image_url
                }
            # Если нет, проверяем продукт
            elif question.product:
                # Проверяем загруженное изображение продукта
                if question.product.image and question.product.image.url:
                    image_data = {
                        "type": "file",
                        "url": question.product.image.url
                    }
                # Проверяем URL изображения продукта
                elif question.product.image_url and question.product.image_url.strip():
                    image_data = {
                        "type": "url",
                        "url": question.product.image_url
                    }
            # ============================================

            return JsonResponse({
                'question_id': question.id,
                'question_text': question.name,
                'difficulty': min_difficulty_level,
                'difficulty_name': question.difficulty.name if question.difficulty else None,
                'product_name': question.product.name if question.product else None,
                'category_name': question.product.category.name if question.product else "Категория",
                'answers': [{"id": a.id, "text": a.text, "is_correct": a.is_correct} for a in answers[:4]],
                'image': image_data,
                'comment': question.comment,
                'reset_occurred': reset_occurred,
                'all_questions_answered': False,
                'has_multiple_answers': len(answers[:4]) > 1
            })

        else:  # Вопрос с изображением (1% случаев)
            # Ищем продукты с изображениями в этой категории
            products_with_images = ZaekProduct.objects.filter(
                category_id=category_id
            ).filter(
                Q(image__isnull=False) & ~Q(image='') |
                Q(image_url__isnull=False) & ~Q(image_url='')
            )

            if not products_with_images.exists():
                # Если нет продуктов с изображениями, показываем обычный вопрос
                question = random.choice(questions)
                answers = list(ZaekAnswer.objects.filter(question=question))
                topic = question.topic

                unique_answers = {}
                for a in answers:
                    if a.text not in unique_answers:
                        unique_answers[a.text] = a

                if len(unique_answers) < 4:
                    additional_answers = ZaekAnswer.objects.filter(
                        question__topic=topic
                    ).exclude(question=question)

                    for a in additional_answers:
                        if a.text not in unique_answers and len(unique_answers) < 4:
                            a.is_correct = False
                            unique_answers[a.text] = a

                answers = list(unique_answers.values())
                random.shuffle(answers)

                # ============ ЛОГИКА ИЗОБРАЖЕНИЙ ============
                image_data = None
                if question.image_url and question.image_url.strip():
                    image_data = {
                        "type": "url",
                        "url": question.image_url
                    }
                elif question.product:
                    if question.product.image and question.product.image.url:
                        image_data = {
                            "type": "file",
                            "url": question.product.image.url
                        }
                    elif question.product.image_url and question.product.image_url.strip():
                        image_data = {
                            "type": "url",
                            "url": question.product.image_url
                        }
                # ============================================

                return JsonResponse({
                    'question_id': question.id,
                    'question_text': question.name,
                    'difficulty': min_difficulty_level,
                    'difficulty_name': question.difficulty.name if question.difficulty else None,
                    'product_name': question.product.name if question.product else None,
                    'category_name': question.product.category.name if question.product else "Категория",
                    'answers': [{"id": a.id, "text": a.text, "is_correct": a.is_correct} for a in answers[:4]],
                    'image': image_data,
                    'comment': question.comment,
                    'reset_occurred': reset_occurred,
                    'all_questions_answered': False,
                    'has_multiple_answers': len(answers[:4]) > 1
                })

            random_product = random.choice(list(products_with_images))

            # Получаем другие продукты для вариантов ответов
            other_products = ZaekProduct.objects.filter(
                category_id=category_id
            ).exclude(id=random_product.id)

            answer_products = random.sample(list(other_products), min(3, len(other_products)))

            answers = [{"id": f"img_{p.id}", "text": p.name, "is_correct": False} for p in answer_products]
            answers.append({"id": f"img_{random_product.id}_correct", "text": random_product.name, "is_correct": True})
            random.shuffle(answers)

            # ============ ЛОГИКА ИЗОБРАЖЕНИЙ ДЛЯ ПРОДУКТА ============
            image_data = None
            # Сначала проверяем загруженное изображение
            if random_product.image and random_product.image.url:
                image_data = {
                    "type": "file",
                    "url": random_product.image.url
                }
            # Затем проверяем URL
            elif random_product.image_url and random_product.image_url.strip():
                image_data = {
                    "type": "url",
                    "url": random_product.image_url
                }
            # =========================================================

            return JsonResponse({
                'question_id': f"image_{random_product.id}",
                'question_text': "Что это за продукт?",
                'difficulty': min_difficulty_level if min_difficulty_level else 1,
                'difficulty_name': None,
                'product_name': '',
                'category_name': random_product.category.name,
                'answers': answers,
                'image': image_data,
                'comment': '',
                'reset_occurred': reset_occurred,
                'all_questions_answered': False,
                'has_multiple_answers': len(answers) > 1,
                'is_image_question': True
            })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_POST
def check_answer_ajax(request):
    """AJAX запрос для проверки ответа"""
    try:
        data = json.loads(request.body)
        question_id = data.get('question_id')
        answer_id = data.get('answer_id')
        telegram_id = str(request.user.id)

        # Проверяем, является ли это вопросом с изображением
        is_image_question = str(question_id).startswith('image_')

        if is_image_question:
            # Для вопросов с изображением
            product_id = str(question_id).replace('image_', '')
            is_correct = str(answer_id).endswith('_correct')

            # Сохраняем в Redis
            if is_correct:
                user_stats_service.add_correct_answer(telegram_id, question_id)

            return JsonResponse({
                'correct': is_correct,
                'comment': None,
                'message': 'Правильно!' if is_correct else 'Неправильно!',
                'correct_answer_id': None
            })

        # Обычный вопрос
        question = get_object_or_404(ZaekQuestion, id=int(question_id))

        # Проверяем ответ
        is_correct = False
        if str(answer_id).isdigit():
            is_correct = question.answers.filter(id=int(answer_id), is_correct=True).exists()

        # Сохраняем в Redis если правильно
        if is_correct:
            user_stats_service.add_correct_answer(telegram_id, question_id)

        # Получаем правильный ответ
        correct_answer = question.answers.filter(is_correct=True).first()

        return JsonResponse({
            'correct': is_correct,
            'comment': question.comment,
            'message': 'Правильно!' if is_correct else 'Неправильно!',
            'correct_answer_id': correct_answer.id if correct_answer else None,
            'correct_answer_text': correct_answer.text if correct_answer else None
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def reset_category(request, category_id):
    """Сброс прогресса по категории"""
    if request.method == 'POST':
        try:
            telegram_id = str(request.user.id)

            # Получаем все вопросы в категории
            questions_in_category = ZaekQuestion.objects.filter(
                product__category_id=category_id
            ).values_list('id', flat=True)

            # Удаляем их из Redis
            user_stats_service.remove_category_questions(telegram_id, list(questions_in_category))

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid method'}, status=400)


# ==================== API ЭНДПОИНТЫ ДЛЯ TELEGRAM ====================

@csrf_exempt
def zaek_user_api(request):
    """API для создания/обновления пользователя"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        telegram_id = data.get('id_telegram')
        name_telegram = data.get('name_telegram')

        return JsonResponse({
            'id_telegram': telegram_id,
            'name_telegram': name_telegram,
            'total_attempts': 0,
            'correct_attempts': 0
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def random_question_api(request):
    """API для получения случайного вопроса"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        question = ZaekQuestion.objects.order_by('?').first()
        if not question:
            return JsonResponse({'error': 'No questions found'}, status=404)

        return JsonResponse({
            'id': question.id,
            'name': question.name,
            'comment': question.comment,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def update_stats_api(request):
    """API для обновления статистики пользователя"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        telegram_id = data.get('telegram_id')
        is_correct = data.get('is_correct')

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# ==================== ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ ====================

def decoder_func(request):
    """Страница декодера"""
    return render(request, 'zaek_app/decoder.html')


def upload_csv(request):
    """Страница загрузки CSV"""
    return render(request, 'zaek_app/upload_csv.html')


def test_func(request):
    """Тестовая страница"""
    return JsonResponse({'status': 'OK', 'message': 'Test endpoint works!'})