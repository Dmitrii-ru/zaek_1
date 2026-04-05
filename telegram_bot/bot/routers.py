from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import random
from zaek.fanc import create_or_get_zaek_user, update_user_stats, safe_send_message, \
    create_reminder, get_today_reminders, delete_reminder, get_all_reminders, get_categories_data, \
    get_categories_question_data
from asgiref.sync import sync_to_async
from core.redis import user_stats_service
from zaek.models import ZaekQuestion

zaek_routers = Router()
max_show_reminders = 12
reminder_rus = "Задачи"

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


@zaek_routers.callback_query(lambda c: c.data == 'categories_question')
async def categories_question_show(callback: types.CallbackQuery):
    categories = await get_categories_data()

    print(categories)

    builder = InlineKeyboardBuilder()
    for category in categories:
        builder.row(InlineKeyboardButton(
            text=category['name'],
            callback_data=f"cqsolo_{category['pk']}"
        ))


    await callback.message.answer(
        text='Список категорий',
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )


class ReminderStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_delete = State()



@zaek_routers.message(ReminderStates.waiting_for_text)
async def process_reminder_text(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if len(text) > 260:
        await message.answer("❌ Текст слишком длинный (максимум 260 символов)")
        return
    result = await create_reminder(str(message.from_user.id), text)
    if result["success"]:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=f"{reminder_rus} на сегодня", callback_data="today_reminders_with_input")]
            ]
        )
        await message.answer(f"✅ Напоминание создано!\n📝 {text}", reply_markup=keyboard)
    else:
        await message.answer("❌ Ошибка при создании напоминания")
    await state.clear()




@zaek_routers.callback_query(lambda c: c.data == "today_reminders_with_input")
async def show_today_reminders_with_input(callback: types.CallbackQuery, state: FSMContext):
    """Показывает список и сразу переходит в режим ввода"""
    result = await get_today_reminders(str(callback.from_user.id))
    if not result["success"]:
        await callback.message.edit_text(
            text=f"❌ {result['error']}",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="reminders_menu")]]
            )
        )
        return

    len_rem = len(result["reminders"])
    reminders = result["reminders"][:max_show_reminders]
    if len_rem <= max_show_reminders:
        text_count_reminders = f'{len_rem}'
    else:
        text_count_reminders = f"{max_show_reminders} из {len_rem}"
    if not reminders:
        text = f"📝 На сегодня {reminder_rus} нет\n\n👇 Напишите вашу первую задачу прямо здесь:"
        keyboard_buttons = []
    else:
        text = f"📋 {reminder_rus} на сегодня ({text_count_reminders}):\n\n"
        keyboard_buttons = []
        current_row = []
        for i, reminder in enumerate(reminders, 1):
            from django.utils import timezone
            time_str = timezone.localtime(reminder.created_at).strftime("%H:%M")
            # Добавляем задачу в текст
            text += f"{i}. {reminder.text} 🕒 {time_str}\n"
            # Добавляем кнопку удаления
            current_row.append(
                InlineKeyboardButton(
                    text=f"❌ {i}",
                    callback_data=f"deletereminder_{reminder.id}"
                )
            )
            # Каждые 3 кнопки создаем новую строку
            if i % 4 == 0:
                keyboard_buttons.append(current_row)
                current_row = []
        if current_row:
            keyboard_buttons.append(current_row)
    # Устанавливаем состояние для ввода
    await state.set_state(ReminderStates.waiting_for_text)
    await state.update_data(original_message_id=callback.message.message_id)
    # Добавляем кнопки навигации
    keyboard_buttons.extend([
        [InlineKeyboardButton(text=f"{reminder_rus} за все время", callback_data="all_reminders_with_input")]
    ])
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    if reminders:
        text += "\n👇 Напишите новую задачу прямо здесь:"
    if len(text) > 4096:
        text = text[:4090] + "..."

    await callback.message.edit_text(text=text, reply_markup=keyboard)


@zaek_routers.callback_query(F.data.startswith("deletereminder_"))
async def process_delete_reminder(callback: types.CallbackQuery, state: FSMContext):
    """Удаляет напоминание и обновляет список"""
    reminder_id = callback.data.split("_")[1]
    result = await delete_reminder(str(callback.from_user.id),reminder_id)

    if result["success"]:
        await callback.answer(f"✅ Удалена задача: {result['deleted_text']}")
        # Обновляем список - вызываем ту же функцию, что показывает список
        await show_all_reminders_with_input(callback)
    else:
        await callback.answer(f"❌ {result['error']}", show_alert=True)

@zaek_routers.callback_query(F.data.startswith("deletereminderall_"))
async def process_delete_reminder(callback: types.CallbackQuery, state: FSMContext):
    """Удаляет напоминание и обновляет список"""
    reminder_id = callback.data.split("_")[1]
    result = await delete_reminder(str(callback.from_user.id),reminder_id)

    if result["success"]:
        await callback.answer(f"✅ Удалена задача: {result['deleted_text']}")
        # Обновляем список - вызываем ту же функцию, что показывает список

        await show_today_reminders_with_input(callback, state)
    else:
        await callback.answer(f"❌ {result['error']}", show_alert=True)


@zaek_routers.callback_query(lambda c: c.data == "all_reminders_with_input")
async def show_all_reminders_with_input(callback: types.CallbackQuery):
    """Показывает список и сразу переходит в режим ввода"""
    result = await get_all_reminders(str(callback.from_user.id))

    if not result["success"]:
        await callback.message.edit_text(
            text=f"❌ {result['error']}",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="Задачи на сегодня", callback_data="today_reminders_with_input")]]
            )
        )
        return

    len_rem = len(result["reminders"])
    reminders = result["reminders"][:max_show_reminders]
    if len_rem <= max_show_reminders:
        text_count_reminders = f'{len_rem}'
    else:
        text_count_reminders = f"{max_show_reminders} из {len_rem}"

    if not reminders:
        text = f"📝 {reminder_rus} нет\n\n👇 Напишите вашу первую задачу прямо здесь:"
        keyboard_buttons = []
    else:
        text = f"📋 {reminder_rus}  ({text_count_reminders}):\n\n"

        keyboard_buttons = []
        current_row = []

        for i, reminder in enumerate(reminders, 1):
            from django.utils import timezone
            time_str = timezone.localtime(reminder.created_at).strftime("%d.%m.%Y %H:%M")
            # Добавляем задачу в текст
            text += f"{i}. {reminder.text} 🕒 {time_str}\n"
            # Добавляем кнопку удаления
            current_row.append(
                InlineKeyboardButton(
                    text=f"❌ {i}",
                    callback_data=f"deletereminder_{reminder.id}"
                )
            )
            # Каждые 3 кнопки создаем новую строку
            if i % 4 == 0:
                keyboard_buttons.append(current_row)
                current_row = []
        if current_row:
            keyboard_buttons.append(current_row)
    keyboard_buttons.extend([
        [InlineKeyboardButton(text=f"{reminder_rus} на сегодня", callback_data="today_reminders_with_input")]
    ])
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    if len(text) > 4096:
        text = text[:4090] + "..."
    await callback.message.edit_text(text=text, reply_markup=keyboard)





#######################################################################################################################
@zaek_routers.callback_query(lambda c: c.data.startswith('answer_'))
async def handle_answer(callback: types.CallbackQuery):
    rout_pref, pref, question_id, is_correct, category_id = callback.data.split('_')
    is_correct = is_correct == 'True'

    if is_correct:
        result_text = "✅ Правильный ответ!"
        if pref != 'image':
            await sync_to_async(user_stats_service.add_correct_answer)(
                str(callback.from_user.id), question_id
            )
    else:
        # Получаем вопрос из базы данных
        question = await sync_to_async(ZaekQuestion.objects.select_related('product').get)(id=question_id)
        result_text = "❌ Неверный ответ!"
        # Проверяем наличие комментария у вопроса
        if question.comment:  # Исправлено: было question.product.comment
            result_text += f"\n\n💡 Комментарий:\n{question.comment}"

    name_telegram = callback.from_user.full_name
    await update_user_stats(str(callback.from_user.id), is_correct, name_telegram)

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Следующий вопрос",
        callback_data=f"cqsolo_{category_id}"
    ))
    builder.row(InlineKeyboardButton(
        text="Выбрать другую категорию",
        callback_data="categories_question"
    ))

    await safe_send_message(
        callback.message,
        result_text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except:
        pass

    await callback.answer()


@zaek_routers.callback_query(F.data.startswith("cqsolo_"))
async def zaek_categories_question(callback: types.CallbackQuery):
    category_id = callback.data.split("_")[1]
    telegram_id = str(callback.from_user.id)
    question_data = await get_categories_question_data(telegram_id, category_id)
    print(category_id)


    if not question_data:
        await callback.answer("Вопросы не найдены", show_alert=True)
        return

    # Проверяем, все ли вопросы в категории отвечены
    if question_data.get('all_questions_answered'):
        category_name = question_data.get('category_name', 'этой категории')

        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(
            text="🎉 Начать заново",
            callback_data=f"reset_category_{category_id}"
        ))
        builder.row(InlineKeyboardButton(
            text="📚 Выбрать другую категорию",
            callback_data="categories_question"
        ))

        congrat_text = (
            f"🎉 Поздравляем! Вы ответили на ВСЕ вопросы категории \"{category_name}\"!\n\n"
            "Вы можете начать эту категорию заново или выбрать другую категорию."
        )

        await callback.message.answer(
            text=congrat_text,
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )

        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except:
            pass

        await callback.answer()
        return

    if question_data.get('reset_occurred'):
        reset_message = (
            f"🎉 Поздравляем! Вы ответили на ВСЕ вопросы верно категории {question_data.get('category_name')}!\n"
            "Начинаем заново! 🚀"
        )
        await callback.message.answer(reset_message)
    # Формируем текст с нумерованными ответами
    str_answer = ""
    for inx, answer in enumerate(question_data['answers']):
        str_answer += f'{inx+1}. {answer["text"]}\n'

    question_text = (
        f"<b>{question_data.get('category_name')}</b>\n"
        f"<b>Продукт:</b> {question_data['product'] if question_data['product'] else 'Не указан'}\n"
        f"<b>Сложность:</b> {question_data['difficulty'] if question_data['difficulty'] else 'Не указана'}\n"
        f"<b>Вопрос:</b> {question_data['question']}\n"
        f'<b>Варианты ответов:</b>\n{str_answer}'
    )

    # Создаем клавиатуру с номерами, включая ID вопроса в callback_data
    builder = InlineKeyboardBuilder()
    for inx, answer in enumerate(question_data['answers']):
        builder.row(InlineKeyboardButton(
            text=str(inx+1),
            callback_data=f"answer_"
                          f"{question_data['question_id']}_"
                          f"{answer['is_correct']}_"
                          f"{question_data['category_id']}"
        ))

    # Обработка изображения
    image_data = question_data.get('image_data')

    if image_data:
        try:
            if image_data['type'] == 'file':
                # Отправляем файл изображения
                from aiogram.types import FSInputFile
                photo = FSInputFile(image_data['image'].path)
                await callback.message.answer_photo(
                    photo=photo,
                    caption=question_text,
                    reply_markup=builder.as_markup(),
                    parse_mode="HTML"
                )

            elif image_data['type'] == 'url':
                # Отправляем изображение по URL
                await callback.message.answer_photo(
                    photo=image_data['url'],
                    caption=question_text,
                    reply_markup=builder.as_markup(),
                    parse_mode="HTML"
                )

        except Exception as e:
            print(f"Ошибка отправки изображения: {str(e)}")
            # Если не удалось отправить изображение, отправляем только текст
            await callback.message.answer(
                text=question_text,
                reply_markup=builder.as_markup(),
                parse_mode="HTML"
            )
    else:
        # Если нет изображения, отправляем только текст
        await safe_send_message(
            callback.message,
            question_text,
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )

    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except:
        pass

    await callback.answer()


@zaek_routers.callback_query(F.data.startswith("reset_category_"))
async def reset_category_questions(callback: types.CallbackQuery):
    """Сбрасывает статистику по категории и начинает заново"""
    category_id = callback.data.split("_")[2]
    telegram_id = str(callback.from_user.id)

    print(category_id,'reset_category_questions')
    # Сбрасываем статистику для этой категории
    category_question_ids = await sync_to_async(list)(
        ZaekQuestion.objects.filter(
            product__category_id=category_id
        ).values_list('id', flat=True)
    )
    await sync_to_async(user_stats_service.remove_category_questions)(telegram_id, category_question_ids)
    # Показываем первый вопрос категории
    await zaek_categories_question(callback)