from asgiref.sync import sync_to_async
import random
from zaek.models import ZaekUser, ZaekQuestion, ZaekAnswer

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
def get_random_question_data():
    """Возвращает данные случайного вопроса с ответами"""
    questions = list(ZaekQuestion.objects.all())
    if not questions:
        return None

    question = random.choice(questions)
    answers = list(ZaekAnswer.objects.filter(question=question))

    return {
        "product": question.product.name if question.product else None,
        "question": question.name,
        "comment": question.comment,
        "answers": [{"text": a.text, "is_correct": a.is_correct} for a in answers]
    }

@sync_to_async
def update_user_stats(telegram_id, is_correct):
    """Обновляет статистику пользователя"""
    user = ZaekUser.objects.get(id_telegram=telegram_id)
    user.total_attempts += 1
    if is_correct:
        user.correct_attempts += 1
    user.save()
    return user