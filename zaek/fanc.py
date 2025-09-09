from asgiref.sync import sync_to_async
import random
from django.db.models import Q
from core.redis import user_stats_service
from zaek.models import ZaekUser, ZaekQuestion, ZaekAnswer, ZaekProduct


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
def get_random_question_data(telegram_id):
    """Возвращает данные вопроса, исключая уже отвеченные верно"""
    answered_questions = user_stats_service.get_answered_questions(telegram_id)
    answered_ids = {int(qid) for qid in answered_questions if qid.isdigit()}
    questions = list(ZaekQuestion.objects.exclude(id__in=answered_ids))
    reset_occurred = False
    if not questions:
        # Если все вопросы отвечены, сбрасываем статистику
        user_stats_service.reset_user_stats(telegram_id)
        questions = list(ZaekQuestion.objects.all())
        reset_occurred = True

    if not questions:
        return None

    number = random.randint(1, 100)
    if number < 85:
        question = random.choice(questions)
        answers = list(ZaekAnswer.objects.filter(question=question))

        # Собираем уникальные ответы
        unique_answers = {}
        for a in answers:
            if a.text not in unique_answers:
                unique_answers[a.text] = a

        # Если не хватает, добираем из связанных вопросов
        if len(unique_answers) < 4:
            if question.product:
                product_answers = ZaekAnswer.objects.filter(
                    question__topic=question.topic
                ).exclude(question=question)
                for a in product_answers:
                    if a.text not in unique_answers and len(unique_answers) < 4:
                        a.is_correct = False
                        unique_answers[a.text] = a

            if len(unique_answers) < 4:
                topic_answers = ZaekAnswer.objects.filter(
                    question__topic=question.topic
                ).exclude(question=question)
                for a in topic_answers:
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
            "question_id": f"question_{question.id}",
            "product": question.product.name if question.product else None,
            "question": question.name,
            "comment": question.comment,
            "image_data": image_data,  # Добавляем изображение для обычных вопросов
            "answers": [{"text": a.text, "is_correct": a.is_correct} for a in answers[:4]],
            "reset_occurred": reset_occurred
        }
    else:
        products_with_images = ZaekProduct.objects.filter(
            Q(image__isnull=False) & ~Q(image='') |
            Q(image_url__isnull=False) & ~Q(image_url='')
        )
        if not products_with_images.exists():
            return None

        random_product = random.choice(products_with_images)
        random_product_name = random_product.name

        answer = [{"text": p.name, "is_correct": False} for p in products_with_images[:3] if
                  p.name != random_product_name]
        true_answer = {"text": random_product.name, "is_correct": True}
        answer.append(true_answer)
        random.shuffle(answer)

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
            "question_id": f"image_{random_product.id}",
            "product": '',
            "question": "Что на фотографии?",
            "comment": '',
            "image_data": image_data,
            "answers": answer,
            "reset_occurred": reset_occurred
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




@sync_to_async
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