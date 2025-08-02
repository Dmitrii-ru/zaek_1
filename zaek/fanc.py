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

    # Проверяем именно 2 ответа (не меньше 4)
    if len(answers) != 2:  # Если ответов не 2, то добираем до 4
        if len(answers) < 4:
            needed = 4 - len(answers)

            # Пробуем взять из связанного продукта (если он есть)
            if question.product:
                product_answers = list(ZaekAnswer.objects.filter(
                    question__product=question.product
                ).exclude(question=question))
                random.shuffle(product_answers)
                answers.extend(product_answers[:needed])
                needed = 4 - len(answers)

            # Если все еще не хватает, берем из той же темы
            if needed > 0:
                topic_answers = list(ZaekAnswer.objects.filter(
                    question__topic=question.topic
                ).exclude(question=question))
                random.shuffle(topic_answers)
                answers.extend(topic_answers[:needed])

    # Перемешиваем ответы перед возвратом
    random.shuffle(answers)

    return {
        "product": question.product.name if question.product else None,
        "question": question.name,
        "comment": question.comment,
        "answers": [{"text": a.text, "is_correct": a.is_correct} for a in answers[:4]]  # Берем максимум 4 ответа
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