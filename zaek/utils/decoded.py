# import base64
# import json
# import re
# import logging
# from django.shortcuts import render
# from zaek.forms import QuizForm
#
# logger = logging.getLogger(__name__)
#
#
# def extract_text(html_string):
#     """Очищает HTML-теги"""
#     if not html_string:
#         return ""
#     return re.sub(r'<[^>]+>', '', html_string).strip()
#
#
# def clean_pres_info(pres_info):
#     """Очищает строку presInfo от лишних пробелов"""
#     pres_info = pres_info.strip()
#     return pres_info
#
#
# def process_matching_question(question):
#     """Обрабатывает вопросы типа Matching (сопоставление)"""
#     try:
#         question_text = extract_text(question['D']['h'])
#
#         matching_data = question['C']['m']
#
#         left_items = []
#         right_items = []
#         correct_pairs = []
#
#         for pair in matching_data:
#             left_text = extract_text(pair['p']['t']['h']) if 'p' in pair and 't' in pair['p'] else ''
#             right_text = extract_text(pair['r']['t']['h']) if 'r' in pair and 't' in pair['r'] else ''
#
#             left_items.append(left_text)
#             right_items.append(right_text)
#
#             correct_pairs.append(f"{left_text} → {right_text}")
#
#         all_choices = []
#         for i, left in enumerate(left_items):
#             all_choices.append({
#                 'text': f"→ {left} → {right_items[i] if i < len(right_items) else '...'}",
#                 'is_correct': True,
#                 'is_matching_pair': True
#             })
#
#         return {
#             'text': question_text,
#             'type': 'Сопоставление',
#             'type_code': 'Matching',
#             'choices': all_choices,
#             'correct_answers': correct_pairs,
#             'has_choices': True,
#             'is_matching': True,
#             'is_numeric': False,
#             'error': False
#         }
#     except Exception as e:
#         logger.error(f"Ошибка обработки matching вопроса: {str(e)}")
#         return {
#             'text': extract_text(question.get('D', {}).get('h', 'Вопрос не распознан')),
#             'type': 'Сопоставление (ошибка)',
#             'type_code': 'Matching',
#             'choices': [],
#             'correct_answers': [f'Ошибка: {str(e)[:100]}'],
#             'has_choices': False,
#             'is_matching': True,
#             'is_numeric': False,
#             'error': True
#         }
#
#
# def process_numeric_question(question):
#     """Обрабатывает вопросы типа Numeric (числовой ответ)"""
#     try:
#         question_text = extract_text(question['D']['h'])
#
#         correct_answers = []
#         if 'C' in question and 'na' in question['C']:
#             for na_item in question['C']['na']:
#                 if 'op' in na_item:
#                     correct_answers.append(na_item['op'])
#                 elif 'co' in na_item and 'op' in na_item:
#                     correct_answers.append(na_item['op'])
#
#         if not correct_answers:
#             if 'D' in question and 'd' in question['D']:
#                 for item in question['D']['d']:
#                     if isinstance(item, dict) and 'data' in item:
#                         if 'v' in item['data']:
#                             correct_answers.extend(item['data']['v'])
#
#         return {
#             'text': question_text,
#             'type': 'Числовой ответ',
#             'type_code': 'Numeric',
#             'choices': [],
#             'correct_answers': correct_answers if correct_answers else ['Нет правильного ответа'],
#             'has_choices': False,
#             'is_matching': False,
#             'is_numeric': True,
#             'error': False
#         }
#     except Exception as e:
#         logger.error(f"Ошибка обработки Numeric вопроса: {str(e)}")
#         return {
#             'text': extract_text(question.get('D', {}).get('h', 'Числовой ответ')),
#             'type': 'Числовой ответ (ошибка)',
#             'type_code': 'Numeric',
#             'choices': [],
#             'correct_answers': [f'Ошибка: {str(e)[:100]}'],
#             'has_choices': False,
#             'is_matching': False,
#             'is_numeric': True,
#             'error': True
#         }
#
#
# def process_multiple_choice_text_question(question):
#     """Обрабатывает вопросы типа MultipleChoiceText (текстовый ответ с вариантами)"""
#     try:
#         question_text = extract_text(question['D']['h'])
#
#         correct_answers = []
#         if 'D' in question and 'd' in question['D']:
#             for item in question['D']['d']:
#                 if isinstance(item, dict) and 'data' in item:
#                     if 'v' in item['data']:
#                         correct_answers.extend(item['data']['v'])
#
#         return {
#             'text': question_text,
#             'type': 'Текстовый ответ',
#             'type_code': 'MultipleChoiceText',
#             'choices': [],
#             'correct_answers': correct_answers if correct_answers else ['Нет правильного ответа'],
#             'has_choices': False,
#             'is_matching': False,
#             'is_numeric': False,
#             'error': False
#         }
#     except Exception as e:
#         logger.error(f"Ошибка обработки MultipleChoiceText: {str(e)}")
#         return {
#             'text': extract_text(question.get('D', {}).get('h', 'Вопрос с ответом')),
#             'type': 'Текстовый ответ (ошибка)',
#             'type_code': 'MultipleChoiceText',
#             'choices': [],
#             'correct_answers': [f'Ошибка: {str(e)[:100]}'],
#             'has_choices': False,
#             'is_matching': False,
#             'is_numeric': False,
#             'error': True
#         }
#
#
# def process_multiple_choice_question(question):
#     """Обрабатывает вопросы с выбором ответа (MultipleChoice, MultipleResponse)"""
#     try:
#         question_text = extract_text(question['D']['h'])
#         q_type = question['tp']
#
#         type_names = {
#             'MultipleChoice': 'Одиночный выбор',
#             'MultipleResponse': 'Множественный выбор',
#             'TrueFalse': 'Верно/Неверно'
#         }
#
#         choices = question['C']['chs']
#         correct_answers = []
#         all_choices = []
#
#         for choice in choices:
#             if 't' not in choice:
#                 continue
#
#             choice_text = extract_text(choice['t'].get('h', ''))
#             is_correct = choice.get('c', False)
#
#             if is_correct:
#                 correct_answers.append(choice_text)
#
#             all_choices.append({
#                 'text': choice_text,
#                 'is_correct': is_correct,
#                 'is_matching_pair': False
#             })
#
#         return {
#             'text': question_text,
#             'type': type_names.get(q_type, q_type),
#             'type_code': q_type,
#             'choices': all_choices,
#             'correct_answers': correct_answers if correct_answers else ['Нет правильного ответа'],
#             'has_choices': len(all_choices) > 0,
#             'is_matching': False,
#             'is_numeric': False,
#             'error': False
#         }
#     except Exception as e:
#         logger.error(f"Ошибка обработки вопроса: {str(e)}")
#         return {
#             'text': extract_text(question.get('D', {}).get('h', 'Вопрос')),
#             'type': 'Ошибка',
#             'type_code': question.get('tp', 'Unknown'),
#             'choices': [],
#             'correct_answers': [f'Ошибка: {str(e)[:100]}'],
#             'has_choices': False,
#             'is_matching': False,
#             'is_numeric': False,
#             'error': True
#         }
#
#
# def safe_process_question(question, q_idx, group_name):
#     """Безопасная обработка вопроса с обработкой ошибок"""
#     try:
#         q_type = question.get('tp', 'Unknown')
#
#         if q_type in ['IntroSlide', 'ResultSlide', 'InfoSlide']:
#             return None
#
#         if 'D' not in question:
#             return {
#                 'text': 'Нет вопроса: отсутствует текст вопроса',
#                 'type': 'Unknown',
#                 'type_code': q_type,
#                 'choices': [],
#                 'correct_answers': ['Ошибка в структуре вопроса'],
#                 'has_choices': False,
#                 'is_matching': False,
#                 'is_numeric': False,
#                 'error': True
#             }
#
#         if q_type == 'Matching':
#             return process_matching_question(question)
#         elif q_type == 'MultipleChoiceText':
#             return process_multiple_choice_text_question(question)
#         elif q_type == 'Numeric':
#             return process_numeric_question(question)
#         elif q_type in ['MultipleChoice', 'MultipleResponse', 'TrueFalse']:
#             return process_multiple_choice_question(question)
#         else:
#             if 'C' in question and 'chs' in question['C']:
#                 return process_multiple_choice_question(question)
#             else:
#                 return {
#                     'text': extract_text(question['D'].get('h', 'Вопрос')),
#                     'type': q_type,
#                     'type_code': q_type,
#                     'choices': [],
#                     'correct_answers': ['Неизвестный тип вопроса'],
#                     'has_choices': False,
#                     'is_matching': False,
#                     'is_numeric': False,
#                     'error': True
#                 }
#
#     except Exception as e:
#         error_msg = str(e)
#         logger.error(f"Ошибка обработки вопроса {q_idx + 1}: {error_msg}")
#         return {
#             'text': f'Не удалось обработать вопрос {q_idx + 1}',
#             'type': 'Ошибка',
#             'type_code': 'Error',
#             'choices': [],
#             'correct_answers': [f'Ошибка: {error_msg[:100]}'],
#             'has_choices': False,
#             'is_matching': False,
#             'is_numeric': False,
#             'error': True
#         }
#
#
# def generate_table_data(result):
#     """
#     Генерирует данные для таблицы в удобном для копирования в Excel формате
#
#     Аргументы:
#         result: dict - результат обработки викторины
#
#     Возвращает:
#         list - список словарей с данными для таблицы
#     """
#     if not result.get('success', False) or not result.get('groups'):
#         return []
#
#     table_rows = []
#
#     for group in result.get('groups', []):
#         group_name = group.get('name', 'Без названия')
#
#         for idx, question in enumerate(group.get('questions', []), 1):
#             # Базовая информация о вопросе
#             row = {
#                 'num': idx,  # Номер вопроса
#                 'group': group_name,  # Группа
#                 'question': question.get('text', ''),  # Текст вопроса
#                 'type': question.get('type', ''),  # Тип вопроса
#                 'correct_answer': ', '.join(question.get('correct_answers', [])) if question.get(
#                     'correct_answers') else '',  # Правильный ответ
#                 'has_error': 'Да' if question.get('error', False) else 'Нет'  # Есть ли ошибка
#             }
#
#             # Собираем варианты ответов в одну строку
#             variants = []
#
#             # Для вопросов с выбором (MultipleChoice, MultipleResponse)
#             if question.get('has_choices', False) and question.get('choices'):
#                 for choice in question['choices']:
#                     prefix = '✅' if choice.get('is_correct', False) else '❌'
#                     variants.append(f"{prefix} {choice.get('text', '')}")
#
#             # Для сопоставления (Matching)
#             if question.get('is_matching', False) and question.get('choices'):
#                 for pair in question['choices']:
#                     variants.append(pair.get('text', ''))
#
#             # Для числовых ответов (Numeric)
#             if question.get('is_numeric', False) and question.get('correct_answers'):
#                 variants.append(f"🔢 {question['correct_answers'][0]}")
#
#             # Добавляем варианты в строку
#             row['variants'] = ' | '.join(variants) if variants else ''
#
#             table_rows.append(row)
#
#     return table_rows
#
#
# def process_json_data(json_data):
#     """Обработка данных из JSON"""
#     result = {
#         'success': True,
#         'groups': [],
#         'total_questions': 0,
#         'errors': []
#     }
#
#     try:
#         if 'd' not in json_data:
#             return {'success': False, 'error': 'Отсутствует корневой элемент: отсутствует поле "d"'}
#
#         if 'sl' not in json_data['d']:
#             return {'success': False, 'error': 'Отсутствует корневой элемент: отсутствует поле "sl"'}
#
#         groups = None
#
#         if 'g' in json_data['d']['sl']:
#             groups = json_data['d']['sl']['g']
#         elif 'g' in json_data['d']:
#             groups = json_data['d']['g']
#
#         if not groups:
#             return {
#                 'success': False,
#                 'error': 'В файле не найдено ни одной группы.',
#                 'groups': [],
#                 'total_questions': 0,
#                 'errors': [{'error': 'Группы вопросов не найдены'}]
#             }
#
#         for group_idx, group in enumerate(groups):
#             try:
#                 group_data = {
#                     'name': group.get('T', f'Группа {group_idx + 1}'),
#                     'questions': []
#                 }
#
#                 questions = group.get('S', [])
#
#                 for q_idx, question in enumerate(questions):
#                     processed_question = safe_process_question(question, q_idx, group_data['name'])
#
#                     if processed_question is None:
#                         continue
#
#                     if not processed_question.get('error', False):
#                         result['total_questions'] += 1
#                     else:
#                         result['errors'].append({
#                             'group': group_data['name'],
#                             'question_index': q_idx + 1,
#                             'error': processed_question.get('correct_answers', ['Неизвестная ошибка'])[0]
#                         })
#
#                     group_data['questions'].append(processed_question)
#
#                 if group_data['questions']:
#                     result['groups'].append(group_data)
#
#             except Exception as e:
#                 error_msg = f"Ошибка обработки группы {group_idx + 1}: {str(e)}"
#                 logger.error(error_msg)
#                 result['errors'].append({
#                     'group': group.get('T', f'Группа {group_idx + 1}'),
#                     'error': error_msg
#                 })
#
#         if not result['groups']:
#             return {
#                 'success': False,
#                 'error': 'В файле не найдено ни одной группы с вопросами.',
#                 'groups': [],
#                 'total_questions': 0,
#                 'errors': result.get('errors', [])
#             }
#
#         if result['errors']:
#             result['success'] = True
#             result['partial_success'] = True
#
#         # Генерируем данные для таблицы
#         result['table_data'] = generate_table_data(result)
#
#         return result
#
#     except Exception as e:
#         error_msg = f"Неизвестная ошибка при обработке JSON: {str(e)}"
#         logger.error(error_msg)
#         return {
#             'success': False,
#             'error': error_msg,
#             'groups': [],
#             'total_questions': 0,
#             'errors': [{'error': error_msg}]
#         }
#
#
# def process_quiz_data(pres_info):
#     """Обработка данных викторины с автоматическим определением формата"""
#     try:
#         pres_info = clean_pres_info(pres_info)
#
#         # Проверяем, не является ли строка уже JSON
#         if pres_info.strip().startswith('{') or pres_info.strip().startswith('['):
#             try:
#                 json_data = json.loads(pres_info)
#                 return process_json_data(json_data)
#             except:
#                 pass
#
#         # Пробуем декодировать Base64
#         try:
#             decoded = base64.b64decode(pres_info)
#         except Exception as e:
#             try:
#                 from urllib.parse import unquote
#                 pres_info = unquote(pres_info)
#                 decoded = base64.b64decode(pres_info)
#             except:
#                 return {
#                     'success': False,
#                     'error': f'Не удалось декодировать данные. Ошибка: {str(e)}',
#                     'groups': [],
#                     'total_questions': 0,
#                     'errors': [{'error': str(e)}]
#                 }
#
#         try:
#             decoded_str = decoded.decode('utf-8')
#         except UnicodeDecodeError:
#             try:
#                 decoded_str = decoded.decode('latin-1')
#             except:
#                 decoded_str = decoded.decode('utf-8', errors='ignore')
#
#         json_data = json.loads(decoded_str)
#         return process_json_data(json_data)
#
#     except Exception as e:
#         error_msg = f"Ошибка обработки: {str(e)}"
#         logger.error(error_msg)
#         return {
#             'success': False,
#             'error': error_msg,
#             'groups': [],
#             'total_questions': 0,
#             'errors': [{'error': error_msg}]
#         }
#
#
# def decoder_func(request):
#     """View для обработки данных викторины"""
#     result = None
#     form = QuizForm()
#
#     if request.method == 'POST':
#         form = QuizForm(request.POST)
#         if form.is_valid():
#             pres_info = form.cleaned_data['pres_info']
#             result = process_quiz_data(pres_info)
#
#     context = {
#         'form': form,
#         'result': result,
#     }
#     return render(request, 'zaek_app/decoder.html', context)

import base64
import json
import re
import logging
from django.shortcuts import render
from zaek.forms import QuizForm

logger = logging.getLogger(__name__)


def extract_text(html_string):
    """Извлекает текст из HTML-строки"""
    if not html_string:
        return ""
    return re.sub(r'<[^>]+>', '', html_string).strip()


def clean_pres_info(pres_info):
    """Очищает строку presInfo от лишних пробелов"""
    pres_info = pres_info.strip()
    return pres_info


def process_matching_question(question):
    """Обрабатывает вопрос типа Matching (соответствие)"""
    try:
        question_text = extract_text(question['D']['h'])

        matching_data = question['C']['m']

        left_items = []
        right_items = []
        correct_pairs = []

        for pair in matching_data:
            left_text = extract_text(pair['p']['t']['h']) if 'p' in pair and 't' in pair['p'] else ''
            right_text = extract_text(pair['r']['t']['h']) if 'r' in pair and 't' in pair['r'] else ''

            left_items.append(left_text)
            right_items.append(right_text)

            correct_pairs.append(f"{left_text} → {right_text}")

        all_choices = []
        for i, left in enumerate(left_items):
            all_choices.append({
                'text': f"→ {left} → {right_items[i] if i < len(right_items) else '...'}",
                'is_correct': True,
                'is_matching_pair': True
            })

        return {
            'text': question_text,
            'type': 'Соответствие',
            'type_code': 'Matching',
            'choices': all_choices,
            'correct_answers': correct_pairs,
            'has_choices': True,
            'is_matching': True,
            'is_numeric': False,
            'error': False
        }
    except Exception as e:
        logger.error(f"Ошибка обработки matching вопроса: {str(e)}")
        return {
            'text': extract_text(question.get('D', {}).get('h', 'Вопрос не найден')),
            'type': 'Соответствие (ошибка)',
            'type_code': 'Matching',
            'choices': [],
            'correct_answers': [f'Ошибка: {str(e)[:100]}'],
            'has_choices': False,
            'is_matching': True,
            'is_numeric': False,
            'error': True
        }


def process_numeric_question(question):
    """Обрабатывает вопрос типа Numeric (числовой ответ)"""
    try:
        question_text = extract_text(question['D']['h'])

        correct_answers = []
        if 'C' in question and 'na' in question['C']:
            for na_item in question['C']['na']:
                if 'op' in na_item:
                    correct_answers.append(str(na_item['op']))
                elif 'co' in na_item and 'op' in na_item:
                    correct_answers.append(str(na_item['op']))

        if not correct_answers:
            if 'D' in question and 'd' in question['D']:
                for item in question['D']['d']:
                    if isinstance(item, dict) and 'data' in item:
                        if 'v' in item['data']:
                            correct_answers.extend([str(v) for v in item['data']['v']])

        return {
            'text': question_text,
            'type': 'Числовой ответ',
            'type_code': 'Numeric',
            'choices': [],
            'correct_answers': correct_answers if correct_answers else ['Нет правильного ответа'],
            'has_choices': False,
            'is_matching': False,
            'is_numeric': True,
            'error': False
        }
    except Exception as e:
        logger.error(f"Ошибка обработки Numeric вопроса: {str(e)}")
        return {
            'text': extract_text(question.get('D', {}).get('h', 'Числовой ответ')),
            'type': 'Числовой ответ (ошибка)',
            'type_code': 'Numeric',
            'choices': [],
            'correct_answers': [f'Ошибка: {str(e)[:100]}'],
            'has_choices': False,
            'is_matching': False,
            'is_numeric': True,
            'error': True
        }


def process_multiple_choice_text_question(question):
    """Обрабатывает вопрос типа MultipleChoiceText (текстовый ответ с вариантами)"""
    try:
        question_text = extract_text(question['D']['h'])

        correct_answers = []
        if 'D' in question and 'd' in question['D']:
            for item in question['D']['d']:
                if isinstance(item, dict) and 'data' in item:
                    if 'v' in item['data']:
                        correct_answers.extend([str(v) for v in item['data']['v']])

        return {
            'text': question_text,
            'type': 'Текстовый ответ',
            'type_code': 'MultipleChoiceText',
            'choices': [],
            'correct_answers': correct_answers if correct_answers else ['Нет правильного ответа'],
            'has_choices': False,
            'is_matching': False,
            'is_numeric': False,
            'error': False
        }
    except Exception as e:
        logger.error(f"Ошибка обработки MultipleChoiceText: {str(e)}")
        return {
            'text': extract_text(question.get('D', {}).get('h', 'Вопрос с текстом')),
            'type': 'Текстовый ответ (ошибка)',
            'type_code': 'MultipleChoiceText',
            'choices': [],
            'correct_answers': [f'Ошибка: {str(e)[:100]}'],
            'has_choices': False,
            'is_matching': False,
            'is_numeric': False,
            'error': True
        }


def process_multiple_choice_question(question):
    """Обрабатывает вопрос с вариантами ответов (MultipleChoice, MultipleResponse)"""
    try:
        question_text = extract_text(question['D']['h'])
        q_type = question['tp']

        type_names = {
            'MultipleChoice': 'Выбор ответа',
            'MultipleResponse': 'Множественный выбор',
            'TrueFalse': 'Правда/Ложь'
        }

        choices = question['C']['chs']
        correct_answers = []
        all_choices = []

        for choice in choices:
            if 't' not in choice:
                continue

            choice_text = extract_text(choice['t'].get('h', ''))
            is_correct = choice.get('c', False)

            if is_correct:
                correct_answers.append(choice_text)

            all_choices.append({
                'text': choice_text,
                'is_correct': is_correct,
                'is_matching_pair': False
            })

        return {
            'text': question_text,
            'type': type_names.get(q_type, q_type),
            'type_code': q_type,
            'choices': all_choices,
            'correct_answers': correct_answers if correct_answers else ['Нет правильного ответа'],
            'has_choices': len(all_choices) > 0,
            'is_matching': False,
            'is_numeric': False,
            'error': False
        }
    except Exception as e:
        logger.error(f"Ошибка обработки вопроса: {str(e)}")
        return {
            'text': extract_text(question.get('D', {}).get('h', 'Вопрос')),
            'type': 'Ошибка',
            'type_code': question.get('tp', 'Unknown'),
            'choices': [],
            'correct_answers': [f'Ошибка: {str(e)[:100]}'],
            'has_choices': False,
            'is_matching': False,
            'is_numeric': False,
            'error': True
        }


def safe_process_question(question, q_idx, group_name):
    """Безопасная обработка вопроса с обработкой ошибок"""
    try:
        q_type = question.get('tp', 'Unknown')

        if q_type in ['IntroSlide', 'ResultSlide', 'InfoSlide']:
            return None

        if 'D' not in question:
            return {
                'text': 'Нет вопроса: отсутствует структура вопроса',
                'type': 'Unknown',
                'type_code': q_type,
                'choices': [],
                'correct_answers': ['Ошибка в структуре вопроса'],
                'has_choices': False,
                'is_matching': False,
                'is_numeric': False,
                'error': True
            }

        if q_type == 'Matching':
            return process_matching_question(question)
        elif q_type == 'MultipleChoiceText':
            return process_multiple_choice_text_question(question)
        elif q_type == 'Numeric':
            return process_numeric_question(question)
        elif q_type in ['MultipleChoice', 'MultipleResponse', 'TrueFalse']:
            return process_multiple_choice_question(question)
        else:
            if 'C' in question and 'chs' in question['C']:
                return process_multiple_choice_question(question)
            else:
                return {
                    'text': extract_text(question['D'].get('h', 'Вопрос')),
                    'type': q_type,
                    'type_code': q_type,
                    'choices': [],
                    'correct_answers': ['Неизвестный тип вопроса'],
                    'has_choices': False,
                    'is_matching': False,
                    'is_numeric': False,
                    'error': True
                }

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Ошибка обработки вопроса {q_idx + 1}: {error_msg}")
        return {
            'text': f'Не удалось обработать вопрос {q_idx + 1}',
            'type': 'Ошибка',
            'type_code': 'Error',
            'choices': [],
            'correct_answers': [f'Ошибка: {error_msg[:100]}'],
            'has_choices': False,
            'is_matching': False,
            'is_numeric': False,
            'error': True
        }


def generate_table_data(result):
    """
    Генерирует данные для таблицы в формате, пригодном для экспорта в Excel

    Аргументы:
        result: dict - результат обработки викторины

    Возвращает:
        list - список строк данных для таблицы
    """
    if not result.get('success', False) or not result.get('groups'):
        return []

    table_rows = []

    for group in result.get('groups', []):
        group_name = group.get('name', 'Без группы')

        for idx, question in enumerate(group.get('questions', []), 1):
            # Собираем информацию в строку
            row = {
                'num': idx,  # Номер вопроса
                'group': group_name,  # Группа
                'question': question.get('text', ''),  # Текст вопроса
                'type': question.get('type', ''),  # Тип вопроса
                'correct_answer': ', '.join(question.get('correct_answers', [])) if question.get(
                    'correct_answers') else '',  # Правильный ответ
                'has_error': 'Да' if question.get('error', False) else 'Нет'  # Есть ли ошибка
            }

            # Собираем варианты ответов в одну строку
            variants = []

            # Для вопросов с вариантами (MultipleChoice, MultipleResponse)
            if question.get('has_choices', False) and question.get('choices'):
                for choice in question['choices']:
                    prefix = '✓' if choice.get('is_correct', False) else '○'
                    variants.append(f"{prefix} {choice.get('text', '')}")

            # Для соответствия (Matching)
            if question.get('is_matching', False) and question.get('choices'):
                for pair in question['choices']:
                    variants.append(pair.get('text', ''))

            # Для числовых ответов (Numeric)
            if question.get('is_numeric', False) and question.get('correct_answers'):
                variants.append(f"→ {question['correct_answers'][0]}")

            # Добавляем варианты в строку
            row['variants'] = ' | '.join(variants) if variants else ''

            table_rows.append(row)

    return table_rows


def process_json_data(json_data):
    """Обрабатывает данные из JSON"""
    result = {
        'success': True,
        'groups': [],
        'total_questions': 0,
        'errors': []
    }

    try:
        if 'd' not in json_data:
            return {'success': False, 'error': 'Некорректная структура данных: отсутствует поле "d"'}

        if 'sl' not in json_data['d']:
            return {'success': False, 'error': 'Некорректная структура данных: отсутствует поле "sl"'}

        groups = None

        if 'g' in json_data['d']['sl']:
            groups = json_data['d']['sl']['g']
        elif 'g' in json_data['d']:
            groups = json_data['d']['g']

        if not groups:
            return {
                'success': False,
                'error': 'В данных не найдено ни одной группы.',
                'groups': [],
                'total_questions': 0,
                'errors': ['Группы вопросов не найдены']
            }

        for group_idx, group in enumerate(groups):
            try:
                group_data = {
                    'name': group.get('T', f'Группа {group_idx + 1}'),
                    'questions': []
                }

                questions = group.get('S', [])

                for q_idx, question in enumerate(questions):
                    processed_question = safe_process_question(question, q_idx, group_data['name'])

                    if processed_question is None:
                        continue

                    if not processed_question.get('error', False):
                        result['total_questions'] += 1
                    else:
                        # ВАЖНО: Добавляем ошибку как строку
                        error_msg = processed_question.get('correct_answers', ['Неизвестная ошибка'])[0]
                        result['errors'].append({
                            'group': group_data['name'],
                            'question_index': q_idx + 1,
                            'error': str(error_msg)  # Принудительно преобразуем в строку
                        })

                    group_data['questions'].append(processed_question)

                if group_data['questions']:
                    result['groups'].append(group_data)

            except Exception as e:
                error_msg = f"Ошибка обработки группы {group_idx + 1}: {str(e)}"
                logger.error(error_msg)
                result['errors'].append({
                    'group': group.get('T', f'Группа {group_idx + 1}'),
                    'error': str(error_msg)  # Принудительно преобразуем в строку
                })

        if not result['groups']:
            return {
                'success': False,
                'error': 'В данных не найдено ни одного вопроса для обработки.',
                'groups': [],
                'total_questions': 0,
                'errors': ['Не найдено ни одного вопроса']
            }

        if result['errors']:
            result['success'] = True
            result['partial_success'] = True

        # Генерируем данные для таблицы
        result['table_data'] = generate_table_data(result)

        # ВАЖНО: Очищаем все ошибки - гарантируем, что это строки
        if 'errors' in result:
            cleaned_errors = []
            for error in result['errors']:
                if isinstance(error, dict):
                    cleaned_error = {}
                    for key, value in error.items():
                        cleaned_error[key] = str(value)  # Принудительно преобразуем всё в строки
                    cleaned_errors.append(cleaned_error)
                else:
                    cleaned_errors.append(str(error))  # Принудительно преобразуем в строку
            result['errors'] = cleaned_errors

        return result

    except Exception as e:
        error_msg = f"Неизвестная ошибка при обработке JSON: {str(e)}"
        logger.error(error_msg)
        return {
            'success': False,
            'error': str(error_msg),  # Принудительно преобразуем в строку
            'groups': [],
            'total_questions': 0,
            'errors': [str(error_msg)]  # Принудительно преобразуем в строку
        }


def process_quiz_data(pres_info):
    """Обрабатывает данные викторины с автоматическим определением формата"""
    try:
        pres_info = clean_pres_info(pres_info)

        # Проверяем, не является ли это уже JSON
        if pres_info.strip().startswith('{') or pres_info.strip().startswith('['):
            try:
                json_data = json.loads(pres_info)
                return process_json_data(json_data)
            except:
                pass

        # Пробуем декодировать Base64
        try:
            decoded = base64.b64decode(pres_info)
        except Exception as e:
            try:
                from urllib.parse import unquote
                pres_info = unquote(pres_info)
                decoded = base64.b64decode(pres_info)
            except:
                return {
                    'success': False,
                    'error': f'Не удалось декодировать данные. Ошибка: {str(e)}',
                    'groups': [],
                    'total_questions': 0,
                    'errors': [str(e)]
                }

        try:
            decoded_str = decoded.decode('utf-8')
        except UnicodeDecodeError:
            try:
                decoded_str = decoded.decode('latin-1')
            except:
                decoded_str = decoded.decode('utf-8', errors='ignore')

        json_data = json.loads(decoded_str)
        return process_json_data(json_data)

    except Exception as e:
        error_msg = f"Ошибка обработки: {str(e)}"
        logger.error(error_msg)
        return {
            'success': False,
            'error': str(error_msg),  # Принудительно преобразуем в строку
            'groups': [],
            'total_questions': 0,
            'errors': [str(error_msg)]  # Принудительно преобразуем в строку
        }


def decoder_func(request):
    """View для обработки данных викторины"""
    result = None
    form = QuizForm()

    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            pres_info = form.cleaned_data['pres_info']
            result = process_quiz_data(pres_info)

    context = {
        'form': form,
        'result': result,
    }
    return render(request, 'zaek_app/decoder.html', context)