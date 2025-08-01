from aiogram import types, Router
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import random
from zaek.fanc import create_or_get_zaek_user, get_random_question_data, update_user_stats

zaek_routers = Router()


@zaek_routers.callback_query(lambda c: c.data == 'user')
async def zaek_user(callback: types.CallbackQuery):
    telegram_id = str(callback.from_user.id)
    name_telegram = callback.from_user.full_name
    # Добавляем await перед вызовом асинхронной функции
    user = await create_or_get_zaek_user(telegram_id, name_telegram)

    await callback.message.edit_text(
        f"{user.get('name_telegram', 'Товарищ')}\n"
        f"Количество попыток: {user['total_attempts']}\n"
        f"Количество верных попыток: {user['correct_attempts']}"
    )


@zaek_routers.callback_query(lambda c: c.data.startswith('answer_'))
async def handle_answer(callback: types.CallbackQuery):
    _, is_correct = callback.data.split('_')
    is_correct = is_correct == 'True'

    result_text = "✅ Правильный ответ!" if is_correct else "❌ Неверный ответ!"
    # Добавляем await перед вызовом асинхронной функции
    await update_user_stats(str(callback.from_user.id), is_correct)

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Следующий вопрос",
        callback_data="question"
    ))

    await callback.message.answer(
        result_text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except:
        pass

    await callback.answer()


@zaek_routers.callback_query(lambda c: c.data == 'question')
async def zaek_question(callback: types.CallbackQuery):
    # Добавляем await перед вызовом асинхронной функции
    question_data = await get_random_question_data()

    if not question_data:
        await callback.answer("Вопросы не найдены", show_alert=True)
        return

    question_text = (
        f"<b>Продукт:</b> {question_data['product'] if question_data['product'] else ''}\n"
        f"<b>Вопрос:</b> {question_data['question']}"
    )

    builder = InlineKeyboardBuilder()
    answers = question_data['answers']
    random.shuffle(answers)

    for answer in answers:
        builder.row(InlineKeyboardButton(
            text=answer['text'],
            callback_data=f"answer_{answer['is_correct']}"
        ))

    await callback.message.answer(
        question_text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except:
        pass

    await callback.answer()