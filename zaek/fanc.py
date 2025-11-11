from asgiref.sync import sync_to_async
import random
from django.db.models import Q
from core.redis import user_stats_service
from zaek.models import ZaekUser, ZaekQuestion, ZaekAnswer, ZaekProduct, Reminder, TopicCategory
from django.db.models import F

# Для всех синхронных функций используем sync_to_async
@sync_to_async
def create_or_get_zaek_user(id_telegram, name_telegram=None):
    """Создает или получает пользователя Zaek"""
    if not id_telegram:
        raise ValueError("id_telegram is required")

    user, created = ZaekUser.objects.get_or_create(
        id_telegram=id_telegram,
        defaults={
            'total_attempts': 0,
            'correct_attempts': 0,
            'show': True,
            'name_telegram': name_telegram
        }
    )
    return {
        'name_telegram': user.name_telegram,
        'total_attempts': user.total_attempts,
        'correct_attempts': user.correct_attempts
    }

@sync_to_async
def get_categories_data():
    all_categoties = list(TopicCategory.objects.values('pk', 'name'))
    return all_categoties


@sync_to_async
def update_user_stats(telegram_id, is_correct,name_telegram):
    """Обновляет статистику пользователя"""
    try:
        user = ZaekUser.objects.get(id_telegram=telegram_id)
    except ZaekUser.DoesNotExist:
        # Создаем пользователя если не существует
        user = ZaekUser.objects.create(
            id_telegram=telegram_id,
            name_telegram=name_telegram,  # Можно позже обновить
            total_attempts=0,
            correct_attempts=0
        )

    user.total_attempts += 1
    if is_correct:
        user.correct_attempts += 1
    user.save()
    return user


async def safe_send_message(message, text, **kwargs):
    """Безопасная отправка сообщений с проверкой длины"""
    max_length = 4096

    if len(text) <= max_length:
        await message.answer(text=text, **kwargs)
    else:
        # Разбиваем текст на части
        parts = []
        current_part = ""

        for line in text.split('\n'):
            if len(current_part) + len(line) + 1 > max_length:
                parts.append(current_part)
                current_part = line
            else:
                if current_part:
                    current_part += '\n' + line
                else:
                    current_part = line

        if current_part:
            parts.append(current_part)

        # Отправляем части без клавиатуры для всех кроме последней
        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                await message.answer(text=part, **kwargs)
            else:
                await message.answer(text=part, parse_mode="HTML")

# Список напоминаний
@sync_to_async
def get_today_reminders(id_telegram):
    """Получает напоминания на сегодня с возможностью удаления"""
    try:
        user = ZaekUser.objects.get(id_telegram=id_telegram)
        from django.utils import timezone
        moscow_time = timezone.localtime(timezone.now())
        today = moscow_time.date()

        reminders = Reminder.objects.filter(
            user=user,
            created_at__date=today
        ).order_by('-created_at')

        return {
            "success": True,
            "reminders": list(reminders),
            "count": len(reminders)
        }
    except ZaekUser.DoesNotExist:
        return {"success": False, "error": "Пользователь не найден"}



@sync_to_async
def create_reminder(id_telegram, text):
    """Создает новое напоминание"""
    try:
        user, created = ZaekUser.objects.get_or_create(id_telegram=id_telegram)
        reminder = Reminder.objects.create(user=user, text=text)
        return {"success": True, "reminder": reminder}
    except Exception as e:
        return {"success": False, "error": str(e)}


@sync_to_async
def create_reminder(id_telegram, text):
    """Создает новое напоминание"""
    try:
        user, created = ZaekUser.objects.get_or_create(id_telegram=id_telegram)
        reminder = Reminder.objects.create(user=user, text=text)
        return {"success": True, "reminder": reminder}
    except Exception as e:
        return {"success": False, "error": str(e)}


@sync_to_async
def delete_reminder(id_telegram, reminder_id):
    """Удаляет напоминание пользователя"""
    try:
        # Находим напоминание по пользователю и ID напоминания
        reminder = Reminder.objects.get(
            user__id_telegram=id_telegram,  # Используем __ для связи с ZaekUser
            id=reminder_id
        )
        reminder_text = reminder.text
        reminder.delete()
        return {"success": True, "deleted_text": reminder_text}
    except Reminder.DoesNotExist:
        return {"success": False, "error": "Напоминание не найдено"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@sync_to_async
def get_all_reminders(id_telegram):
    """Получает напоминания на сегодня с возможностью удаления"""
    try:
        user = ZaekUser.objects.get(id_telegram=id_telegram)

        reminders = Reminder.objects.filter(
            user=user,
        ).order_by('-created_at')

        return {
            "success": True,
            "reminders": list(reminders),
            "count": len(reminders)
        }

    except ZaekUser.DoesNotExist:
        return {"success": False, "error": "Пользователь не найден"}


#####################################################################################################
@sync_to_async
def get_categories_question_data(telegram_id, category_id):
    """Возвращает данные вопроса, исключая уже отвеченные верно"""
    answered_questions = user_stats_service.get_answered_questions(telegram_id)
    answered_ids = {int(qid) for qid in answered_questions if qid.isdigit()}

    # Получаем вопросы для категории через продукты
    questions = ZaekQuestion.objects.filter(
        product__category_id=category_id
    ).exclude(
        id__in=answered_ids
    ).annotate(
        difficulty_level=F('difficulty__level')
    ).order_by(
        'difficulty_level',
    )

    # Инициализируем переменную
    min_difficulty_level = None
    reset_occurred = False

    # Получаем первый вопрос для определения минимального уровня сложности
    if questions.exists():
        first_question = questions.first()
        min_difficulty_level = first_question.difficulty_level
        # Берем все вопросы с минимальным уровнем сложности
        questions = [obj for obj in questions if obj.difficulty_level == min_difficulty_level]
    else:
        questions = []

    if not questions:
        # Если все вопросы отвечены, сбрасываем статистику
        category_question_ids = ZaekQuestion.objects.filter(
            product__category_id=category_id
        ).values_list('id', flat=True)
        user_stats_service.remove_category_questions(telegram_id, category_question_ids)
        questions = list(ZaekQuestion.objects.filter(product__category_id=category_id))
        reset_occurred = True

        # После сброса снова определяем минимальный уровень сложности
        if questions:
            questions_with_difficulty = ZaekQuestion.objects.filter(
                product__category_id=category_id
            ).annotate(
                difficulty_level=F('difficulty__level')
            ).order_by('difficulty_level')

            if questions_with_difficulty.exists():
                min_difficulty_level = questions_with_difficulty.first().difficulty_level
                questions = [obj for obj in questions_with_difficulty if obj.difficulty_level == min_difficulty_level]

    if not questions:
        return None

    number = random.randint(1, 100)
    if number < 100:  # Обычные вопросы
        question = random.choice(questions)
        answers = list(ZaekAnswer.objects.filter(question=question))
        topic = question.topic

        # Собираем уникальные ответы
        unique_answers = {}
        for a in answers:
            if a.text not in unique_answers:
                unique_answers[a.text] = a

        # Если не хватает, добираем из связанных вопросов
        if len(unique_answers) < 4:
            # Добираем ответы из вопросов той же сложности и категории
            additional_answers = ZaekAnswer.objects.filter(
                question__topic=topic
            ).exclude(question=question)

            for a in additional_answers:
                if a.text not in unique_answers and len(unique_answers) < 4:
                    a.is_correct = False
                    unique_answers[a.text] = a

        answers = list(unique_answers.values())
        random.shuffle(answers)

        # Определяем данные изображения для обычного вопроса
        image_data = None
        if question.product:
            # Пытаемся получить изображение из связанного продукта
            if question.product.image:
                image_data = {
                    "type": "file",
                    "image": question.product.image
                }
            elif question.product.image_url:
                image_data = {
                    "type": "url",
                    "url": question.product.image_url
                }

        return {
            'difficulty': min_difficulty_level,
            'category_id': category_id,
            "question_id": f"question_{question.id}",
            "product": question.product.name if question.product else None,
            "question": question.name,
            "comment": question.comment,
            "image_data": image_data,
            "answers": [{"text": a.text, "is_correct": a.is_correct} for a in answers[:4]],
            "reset_occurred": reset_occurred,
            "category_name": question.product.category.name if question.product else "Общая"
        }
    else:  # Вопросы с изображением
        # Для вопросов с изображением также определяем уровень сложности
        if min_difficulty_level is None:
            # Если нет обычных вопросов, берем минимальный уровень из всех вопросов категории
            min_difficulty_question = ZaekQuestion.objects.filter(
                product__category_id=category_id
            ).annotate(
                difficulty_level=F('difficulty__level')
            ).order_by('difficulty_level').first()

            if min_difficulty_question:
                min_difficulty_level = min_difficulty_question.difficulty_level
            else:
                min_difficulty_level = 1  # Значение по умолчанию

        products_with_images = ZaekProduct.objects.filter(
            category_id=category_id
        ).filter(
            Q(image__isnull=False) & ~Q(image='') |
            Q(image_url__isnull=False) & ~Q(image_url='')
        )

        if not products_with_images.exists():
            return None

        random_product = random.choice(list(products_with_images))
        random_product_name = random_product.name

        # Создаем варианты ответов из других продуктов этой категории
        other_products = ZaekProduct.objects.filter(
            category_id=category_id
        ).exclude(id=random_product.id)

        answer_products = random.sample(list(other_products), min(3, len(other_products)))

        answers = [{"text": p.name, "is_correct": False} for p in answer_products]
        answers.append({"text": random_product.name, "is_correct": True})
        random.shuffle(answers)

        image_data = None
        if random_product.image:
            image_data = {
                "type": "file",
                "image": random_product.image
            }
        elif random_product.image_url:
            image_data = {
                "type": "url",
                "url": random_product.image_url
            }

        return {
            'difficulty': min_difficulty_level,
            'category_id': category_id,
            "question_id": f"image_{random_product.id}",
            "product": '',
            "question": "Что на фотографии?",
            "comment": '',
            "image_data": image_data,
            "answers": answers,
            "reset_occurred": reset_occurred,
            "category_name": random_product.category.name
        }