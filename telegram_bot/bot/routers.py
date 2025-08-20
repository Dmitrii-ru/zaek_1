from aiogram import types, Router
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import random
from zaek.fanc import create_or_get_zaek_user, get_random_question_data, update_user_stats
from asgiref.sync import sync_to_async
from core.redis import user_stats_service
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
    rout_pref,pref, question_id, is_correct = callback.data.split('_')
    is_correct = is_correct == 'True'

    if is_correct:
        result_text = "✅ Правильный ответ!"
        if pref!='image':
            await sync_to_async(user_stats_service.add_correct_answer)(
                str(callback.from_user.id), question_id
            )
    else:
        result_text = "❌ Неверный ответ!"


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
    telegram_id = str(callback.from_user.id)
    question_data = await get_random_question_data(telegram_id)

    if not question_data:
        await callback.answer("Вопросы не найдены", show_alert=True)
        return

    if question_data.get('reset_occurred'):
        reset_message = (
            "🎉 Поздравляем! Вы ответили на ВСЕ вопросы верно!\n"
            "Начинаем заново! 🚀"
        )
        await callback.message.answer(reset_message)


    # Формируем текст с нумерованными ответами
    str_answer = ""
    for inx, answer in enumerate(question_data['answers']):
        str_answer += f'{inx+1}. {answer["text"]}\n'

    question_text = (
        f"<b>Продукт:</b> {question_data['product'] if question_data['product'] else ''}\n\n"
        f"<b>Вопрос:</b> {question_data['question']}\n\n"
        f'<b>Варианты ответов:</b>\n{str_answer}'
    )

    # Создаем клавиатуру с номерами, включая ID вопроса в callback_data
    builder = InlineKeyboardBuilder()
    for inx, answer in enumerate(question_data['answers']):
        builder.row(InlineKeyboardButton(
            text=str(inx+1),
            callback_data=f"answer_{question_data['question_id']}_{answer['is_correct']}"
        ))

    # Обработка изображения
    if question_data.get('image'):
        try:
            from aiogram.types import FSInputFile
            photo = FSInputFile(question_data['image'].path)
            await callback.message.answer_photo(
                photo=photo,
                caption=question_text,
                reply_markup=builder.as_markup(),
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"Ошибка отправки изображения: {str(e)}")
            await callback.message.answer(
                text=question_text,
                reply_markup=builder.as_markup(),
                parse_mode="HTML"
            )
    else:
        await callback.message.answer(
            text=question_text,
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )

    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except:
        pass

    await callback.answer()
