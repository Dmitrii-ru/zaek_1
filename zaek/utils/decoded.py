# # # import base64
# # # import json
# # # import re
# # # import sys
# # # import io
# # #
# # # sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# # #
# # #
# # # # def decoder_func(text):
# # # # ВСТАВЬТЕ СЮДА ВСЮ СТРОКУ presInfo (она начинается с "eNrtfWlzHMc...")
# # # #     presInfo = f"{text}"
# # # #     json_data =''
# # # #     # Шаг 1: Декодируем Base64
# # # #     try:
# # # #         decoded = base64.b64decode(presInfo)
# # # #         print(f"✅ Base64 декодирован. Размер: {len(decoded)} байт")
# # # #
# # # #         # Шаг 2: Пробуем распарсить как JSON
# # # #         try:
# # # #             json_data = json.loads(decoded.decode('utf-8'))
# # # #             print("✅ Данные в формате JSON!")
# # # #             print(json.dumps(json_data, indent=2, ensure_ascii=False)[:500])
# # # #         except:
# # # #             print("❌ Не JSON. Проверяем, может быть сжато...")
# # # #
# # # #             # Шаг 3: Пробуем распаковать GZIP
# # # #             try:
# # # #                 import gzip
# # # #                 import io
# # # #
# # # #                 decompressed = gzip.decompress(decoded)
# # # #                 try:
# # # #                     json_data = json.loads(decompressed.decode('utf-8'))
# # # #                     print("✅ Данные сжаты GZIP + JSON!")
# # # #                     print(json.dumps(json_data, indent=2, ensure_ascii=False)[:500])
# # # #                 except:
# # # #                     print("Данные распакованы, но не JSON:")
# # # #                     print(decompressed[:200])
# # # #             except:
# # # #                 print("❌ Не GZIP. Пробуем ZLIB...")
# # # #
# # # #                 # Шаг 4: Пробуем распаковать ZLIB
# # # #                 try:
# # # #                     decompressed = zlib.decompress(decoded)
# # # #                     try:
# # # #                         json_data = json.loads(decompressed.decode('utf-8'))
# # # #                         print("✅ Данные сжаты ZLIB + JSON!")
# # # #                         print(json.dumps(json_data, indent=2, ensure_ascii=False)[:500])
# # # #                     except:
# # # #                         print("Данные распакованы, но не JSON:")
# # # #                         print(decompressed[:200])
# # # #                 except Exception as e:
# # # #                     print(f"❌ Не удалось распаковать: {e}")
# # # #                     print("\nПробуем декодировать как текст (может быть бинарные данные):")
# # # #                     try:
# # # #                         text = decoded.decode('utf-8', errors='ignore')
# # # #                         print(text[:500])
# # # #                     except:
# # # #                         print("Не удалось декодировать как текст")
# # # #
# # # #     except Exception as e:
# # # #         print(f"❌ Ошибка: {e}")
# # # #
# # # #     import re
# # # #     def extract_text(html_string):
# # # #         """Удаляет HTML-теги"""
# # # #         if not html_string:
# # # #             return ""
# # # #         return re.sub(r'<[^>]+>', '', html_string).strip()
# # # #
# # # #
# # # #     # Получаем группы вопросов
# # # #     groups = json_data['d']['sl']['g']
# # # #
# # # #     print(f"Найдено групп: {len(groups)}")
# # # #     print("=" * 70)
# # # #
# # # #     for group_idx, group in enumerate(groups):
# # # #         group_name = group.get('T', f'Группа {group_idx + 1}')
# # # #         print(f"\n{'=' * 70}")
# # # #         print(f"📚 ГРУППА: {group_name}")
# # # #         print(f"{'=' * 70}")
# # # #
# # # #         # Получаем вопросы из группы
# # # #         questions = group.get('S', [])
# # # #         print(f"Вопросов в группе: {len(questions)}\n")
# # # #
# # # #         for q_idx, question in enumerate(questions):
# # # #             print(f"\n{'─' * 70}")
# # # #             print(f"❓ ВОПРОС {q_idx + 1}")
# # # #             print(f"{'─' * 70}")
# # # #
# # # #             # Текст вопроса
# # # #             question_html = question['D']['h']
# # # #             question_text = extract_text(question_html)
# # # #             print(f"📝 {question_text}")
# # # #
# # # #             # Тип вопроса
# # # #             q_type = question['tp']
# # # #             type_names = {
# # # #                 'MultipleChoice': 'Одиночный выбор',
# # # #                 'MultipleResponse': 'Множественный выбор',
# # # #                 'TrueFalse': 'Верно/Неверно'
# # # #             }
# # # #             print(f"📌 Тип: {type_names.get(q_type, q_type)}")
# # # #
# # # #             # Получаем варианты ответов
# # # #             choices = question['C']['chs']
# # # #             correct_answers = []
# # # #
# # # #             print(f"\n📋 Варианты ответов:")
# # # #             for choice_idx, choice in enumerate(choices, 1):
# # # #                 choice_text = extract_text(choice['t']['h'])
# # # #                 is_correct = choice.get('c', False)
# # # #
# # # #                 if is_correct:
# # # #                     correct_answers.append(choice_text)
# # # #                     print(f"  {choice_idx}. ✅ {choice_text} (ПРАВИЛЬНЫЙ)")
# # # #                 else:
# # # #                     print(f"  {choice_idx}. ❌ {choice_text}")
# # # #
# # # #             # Выводим правильные ответы
# # # #             print()
# # # #             if correct_answers:
# # # #                 if len(correct_answers) == 1:
# # # #                     print(f"🎯 ПРАВИЛЬНЫЙ ОТВЕТ: {correct_answers[0]}")
# # # #                 else:
# # # #                     print(f"🎯 ПРАВИЛЬНЫЕ ОТВЕТЫ: {', '.join(correct_answers)}")
# # # #             else:
# # # #                 print("⚠️ Нет правильных ответов")
# # # #
# # # #             print(f"{'─' * 70}")
# # # #     #     print('-',i)
# # # #     #     for z in i:
# # # #     #         print('--',z)
# # # #     #         for g in z:
# # # #     #             print('---',g)
# # # #     #
# # # #     # print(json_data['d']['sl'])
# # # #
# # # #     # def find_quiz_data(obj, path=""):
# # # #     #     if isinstance(obj, dict):
# # # #     #         for key, value in obj.items():
# # # #     #             new_path = f"{path}.{key}" if path else key
# # # #     #             # Ищем ключи, которые могут содержать вопросы
# # # #     #             if key in ['questions', 'quiz', 'quizData', 'items', 'answers', 'correct']:
# # # #     #                 print(f"🔍 Найден ключ: {new_path}")
# # # #     #                 print(f"   Содержит: {type(value)}")
# # # #     #                 if isinstance(value, list):
# # # #     #                     print(f"   Длина: {len(value)}")
# # # #     #                     if len(value) > 0:
# # # #     #                         print(f"   Пример: {str(value[0])[:300]}")
# # # #     #                 elif isinstance(value, dict):
# # # #     #                     print(f"   Ключи: {list(value.keys())[:10]}")
# # # #     #                 print("-" * 60)
# # # #     #             find_quiz_data(value, new_path)
# # # #     #     elif isinstance(obj, list):
# # # #     #         for i, item in enumerate(obj):
# # # #     #             find_quiz_data(item, f"{path}[{i}]")
# # # #     #
# # # #     #
# # # #     # find_quiz_data(json_data)
# # # #     # # Рекурсивно выведем все ключи на глубину до 3 уровней
# # # #     # def print_structure(obj, depth=0, max_depth=3):
# # # #     #     if depth > max_depth:
# # # #     #         return
# # # #     #     indent = "  " * depth
# # # #     #     if isinstance(obj, dict):
# # # #     #         for key, value in obj.items():
# # # #     #             print(f"{indent}{key}: {type(value).__name__}")
# # # #     #             if isinstance(value, (dict, list)):
# # # #     #                 print_structure(value, depth + 1, max_depth)
# # # #     #     elif isinstance(obj, list):
# # # #     #         if obj:
# # # #     #             print(f"{indent}список из {len(obj)} элементов")
# # # #     #             print_structure(obj[0], depth + 1, max_depth)
# # # #     #
# # # #     # print("Полная структура json_data['d']:")
# # # # print_structure(json_data['d'])
# # #
# # # import base64
# # # import json
# # # import re
# # # from django.shortcuts import render
# # # from django.http import JsonResponse
# # # from zaek.forms import QuizForm
# # #
# # #
# # # def extract_text(html_string):
# # #     """Удаляет HTML-теги"""
# # #     if not html_string:
# # #         return ""
# # #     return re.sub(r'<[^>]+>', '', html_string).strip()
# # #
# # #
# # # def process_quiz_data(pres_info):
# # #     """Обрабатывает данные викторины и возвращает структурированный результат"""
# # #     try:
# # #         # Декодируем Base64
# # #         decoded = base64.b64decode(pres_info)
# # #         json_data = json.loads(decoded.decode('utf-8'))
# # #
# # #         # Получаем группы вопросов
# # #         groups = json_data['d']['sl']['g']
# # #
# # #         result = {
# # #             'success': True,
# # #             'groups': [],
# # #             'total_questions': 0
# # #         }
# # #
# # #         for group in groups:
# # #             group_data = {
# # #                 'name': group.get('T', 'Без названия'),
# # #                 'questions': []
# # #             }
# # #
# # #             questions = group.get('S', [])
# # #             result['total_questions'] += len(questions)
# # #
# # #             for question in questions:
# # #                 question_text = extract_text(question['D']['h'])
# # #                 q_type = question['tp']
# # #
# # #                 type_names = {
# # #                     'MultipleChoice': 'Одиночный выбор',
# # #                     'MultipleResponse': 'Множественный выбор',
# # #                     'TrueFalse': 'Верно/Неверно'
# # #                 }
# # #
# # #                 choices = question['C']['chs']
# # #                 correct_answers = []
# # #                 all_choices = []
# # #
# # #                 for choice in choices:
# # #                     choice_text = extract_text(choice['t']['h'])
# # #                     is_correct = choice.get('c', False)
# # #
# # #                     if is_correct:
# # #                         correct_answers.append(choice_text)
# # #
# # #                     all_choices.append({
# # #                         'text': choice_text,
# # #                         'is_correct': is_correct
# # #                     })
# # #
# # #                 group_data['questions'].append({
# # #                     'text': question_text,
# # #                     'type': type_names.get(q_type, q_type),
# # #                     'type_code': q_type,
# # #                     'choices': all_choices,
# # #                     'correct_answers': correct_answers
# # #                 })
# # #
# # #             result['groups'].append(group_data)
# # #
# # #         return result
# # #
# # #     except Exception as e:
# # #         return {
# # #             'success': False,
# # #             'error': str(e)
# # #         }
# # #
# # #
# # # def decoder_func(request):
# # #     """View для обработки данных викторины"""
# # #     result = None
# # #     form = QuizForm()
# # #
# # #     if request.method == 'POST':
# # #         form = QuizForm(request.POST)
# # #         if form.is_valid():
# # #             pres_info = form.cleaned_data['pres_info']
# # #             result = process_quiz_data(pres_info)
# # #
# # #     context = {
# # #         'form': form,
# # #         'result': result,
# # #     }
# # #     return render(request, 'zaek_app/decoder.html', context)
# #
# #
# # import base64
# # import json
# # import re
# # from django.shortcuts import render
# # from .forms import QuizForm
# #
# #
# # def extract_text(html_string):
# #     """Удаляет HTML-теги"""
# #     if not html_string:
# #         return ""
# #     return re.sub(r'<[^>]+>', '', html_string).strip()
# #
# #
# # def clean_pres_info(pres_info):
# #     """Очищает строку presInfo от лишних символов"""
# #     # Удаляем пробелы в начале и конце
# #     pres_info = pres_info.strip()
# #
# #     # Если строка начинается с "eyJ", это скорее всего Base64
# #     # Но могут быть и другие варианты
# #     return pres_info
# #
# #
# # def process_quiz_data(pres_info):
# #     """Обрабатывает данные викторины и возвращает структурированный результат"""
# #     try:
# #         # Очищаем строку
# #         pres_info = clean_pres_info(pres_info)
# #
# #         # Пробуем декодировать Base64
# #         try:
# #             # Стандартное декодирование
# #             decoded = base64.b64decode(pres_info)
# #         except Exception as e:
# #             # Если не получилось, возможно строка содержит URL-encoded символы
# #             try:
# #                 from urllib.parse import unquote
# #                 pres_info = unquote(pres_info)
# #                 decoded = base64.b64decode(pres_info)
# #             except:
# #                 # Если все еще ошибка, возможно это не Base64, а уже JSON
# #                 if pres_info.startswith('{') or pres_info.startswith('['):
# #                     json_data = json.loads(pres_info)
# #                     return process_json_data(json_data)
# #                 raise ValueError(f"Не удалось декодировать данные: {e}")
# #
# #         # Пробуем декодировать как UTF-8
# #         try:
# #             decoded_str = decoded.decode('utf-8')
# #         except UnicodeDecodeError:
# #             # Если UTF-8 не подходит, пробуем другие кодировки
# #             try:
# #                 decoded_str = decoded.decode('latin-1')
# #             except:
# #                 decoded_str = decoded.decode('utf-8', errors='ignore')
# #
# #         # Парсим JSON
# #         json_data = json.loads(decoded_str)
# #         return process_json_data(json_data)
# #
# #     except Exception as e:
# #         return {
# #             'success': False,
# #             'error': f"Ошибка обработки: {str(e)}"
# #         }
# #
# #
# # def process_json_data(json_data):
# #     """Обрабатывает уже декодированный JSON"""
# #     try:
# #         # Проверяем структуру
# #         if 'd' not in json_data:
# #             return {'success': False, 'error': 'Неверная структура данных: отсутствует ключ "d"'}
# #
# #         if 'sl' not in json_data['d']:
# #             return {'success': False, 'error': 'Неверная структура данных: отсутствует ключ "sl"'}
# #
# #         if 'g' not in json_data['d']['sl']:
# #             return {'success': False, 'error': 'Неверная структура данных: отсутствует ключ "g"'}
# #
# #         groups = json_data['d']['sl']['g']
# #
# #         result = {
# #             'success': True,
# #             'groups': [],
# #             'total_questions': 0
# #         }
# #
# #         for group in groups:
# #             group_data = {
# #                 'name': group.get('T', 'Без названия'),
# #                 'questions': []
# #             }
# #
# #             questions = group.get('S', [])
# #             result['total_questions'] += len(questions)
# #
# #             for question in questions:
# #                 question_text = extract_text(question['D']['h'])
# #                 q_type = question['tp']
# #
# #                 type_names = {
# #                     'MultipleChoice': 'Одиночный выбор',
# #                     'MultipleResponse': 'Множественный выбор',
# #                     'TrueFalse': 'Верно/Неверно'
# #                 }
# #
# #                 choices = question['C']['chs']
# #                 correct_answers = []
# #                 all_choices = []
# #
# #                 for choice in choices:
# #                     choice_text = extract_text(choice['t']['h'])
# #                     is_correct = choice.get('c', False)
# #
# #                     if is_correct:
# #                         correct_answers.append(choice_text)
# #
# #                     all_choices.append({
# #                         'text': choice_text,
# #                         'is_correct': is_correct
# #                     })
# #
# #                 group_data['questions'].append({
# #                     'text': question_text,
# #                     'type': type_names.get(q_type, q_type),
# #                     'type_code': q_type,
# #                     'choices': all_choices,
# #                     'correct_answers': correct_answers
# #                 })
# #
# #             result['groups'].append(group_data)
# #
# #         return result
# #
# #     except Exception as e:
# #         return {
# #             'success': False,
# #             'error': f"Ошибка обработки JSON: {str(e)}"
# #         }
# #
# #
# # def decoder_func(request):
# #     """View для обработки данных викторины"""
# #     result = None
# #     form = QuizForm()
# #
# #     if request.method == 'POST':
# #         form = QuizForm(request.POST)
# #         if form.is_valid():
# #             pres_info = form.cleaned_data['pres_info']
# #             result = process_quiz_data(pres_info)
# #
# #     context = {
# #         'form': form,
# #         'result': result,
# #     }
# #     return render(request, 'zaek_app/decoder.html', context)
#
#
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
#     """Удаляет HTML-теги"""
#     if not html_string:
#         return ""
#     return re.sub(r'<[^>]+>', '', html_string).strip()
#
#
# def clean_pres_info(pres_info):
#     """Очищает строку presInfo от лишних символов"""
#     pres_info = pres_info.strip()
#     return pres_info
#
#
# def process_matching_question(question):
#     """Обрабатывает вопрос типа Matching (сопоставление)"""
#     try:
#         question_text = extract_text(question['D']['h'])
#
#         # Получаем пары для сопоставления
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
#             # В matching правильные пары определяются по индексам
#             # left_item → right_item
#             correct_pairs.append(f"{left_text} → {right_text}")
#
#         # Формируем список вариантов для отображения
#         all_choices = []
#         for i, left in enumerate(left_items):
#             all_choices.append({
#                 'text': f"📌 {left} → {right_items[i] if i < len(right_items) else '...'}",
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
#             'error': False
#         }
#     except Exception as e:
#         logger.error(f"Ошибка обработки matching вопроса: {str(e)}")
#         return {
#             'text': extract_text(question.get('D', {}).get('h', 'Вопрос на сопоставление')),
#             'type': 'Сопоставление (ошибка)',
#             'type_code': 'Matching',
#             'choices': [],
#             'correct_answers': [f'Ошибка: {str(e)[:100]}'],
#             'has_choices': False,
#             'is_matching': True,
#             'error': True
#         }
#
#
# def process_multiple_choice_question(question):
#     """Обрабатывает вопросы с вариантами ответов (MultipleChoice, MultipleResponse)"""
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
#             'correct_answers': correct_answers if correct_answers else ['Нет правильных ответов'],
#             'has_choices': len(all_choices) > 0,
#             'is_matching': False,
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
#             'error': True
#         }
#
#
# def process_multiple_choice_text_question(question):
#     """Обрабатывает вопрос типа MultipleChoiceText (вставка текста в пропуски)"""
#     try:
#         question_text = extract_text(question['D']['h'])
#
#         # Извлекаем правильные ответы из D.d
#         correct_answers = []
#         if 'D' in question and 'd' in question['D']:
#             for item in question['D']['d']:
#                 if isinstance(item, dict) and 'data' in item:
#                     # Для MultipleChoiceText правильные ответы в data.v
#                     if 'v' in item['data']:
#                         correct_answers.extend(item['data']['v'])
#
#         return {
#             'text': question_text,
#             'type': 'Вставка текста',
#             'type_code': 'MultipleChoiceText',
#             'choices': [],
#             'correct_answers': correct_answers if correct_answers else ['Нет правильных ответов'],
#             'has_choices': False,
#             'is_matching': False,
#             'error': False
#         }
#     except Exception as e:
#         logger.error(f"Ошибка обработки MultipleChoiceText: {str(e)}")
#         return {
#             'text': extract_text(question.get('D', {}).get('h', 'Вопрос с пропусками')),
#             'type': 'Вставка текста (ошибка)',
#             'type_code': 'MultipleChoiceText',
#             'choices': [],
#             'correct_answers': [f'Ошибка: {str(e)[:100]}'],
#             'has_choices': False,
#             'is_matching': False,
#             'error': True
#         }
#
#
# def safe_process_question(question, q_idx, group_name):
#     """Безопасная обработка одного вопроса с перехватом ошибок"""
#     try:
#         q_type = question.get('tp', 'Unknown')
#
#         # Пропускаем слайды, которые не являются вопросами
#         if q_type in ['IntroSlide', 'ResultSlide', 'InfoSlide']:
#             return None
#
#         # Проверяем наличие ключа 'D'
#         if 'D' not in question:
#             return {
#                 'text': '⚠️ Ошибка: отсутствует текст вопроса',
#                 'type': 'Unknown',
#                 'type_code': q_type,
#                 'choices': [],
#                 'correct_answers': ['Ошибка в структуре вопроса'],
#                 'has_choices': False,
#                 'is_matching': False,
#                 'error': True
#             }
#
#         # Обработка разных типов вопросов
#         if q_type == 'Matching':
#             return process_matching_question(question)
#         elif q_type == 'MultipleChoiceText':
#             return process_multiple_choice_text_question(question)
#         elif q_type in ['MultipleChoice', 'MultipleResponse', 'TrueFalse']:
#             return process_multiple_choice_question(question)
#         else:
#             # Для неизвестных типов пытаемся обработать как MultipleChoice
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
#                     'error': True
#                 }
#
#     except Exception as e:
#         error_msg = str(e)
#         logger.error(f"Ошибка обработки вопроса {q_idx + 1}: {error_msg}")
#         return {
#             'text': f'⚠️ Ошибка обработки вопроса {q_idx + 1}',
#             'type': 'Ошибка',
#             'type_code': 'Error',
#             'choices': [],
#             'correct_answers': [f'Ошибка: {error_msg[:100]}'],
#             'has_choices': False,
#             'is_matching': False,
#             'error': True
#         }
#
#
# def process_json_data(json_data):
#     """Обрабатывает уже декодированный JSON"""
#     result = {
#         'success': True,
#         'groups': [],
#         'total_questions': 0,
#         'errors': []
#     }
#
#     try:
#         # Проверяем структуру
#         if 'd' not in json_data:
#             return {'success': False, 'error': 'Неверная структура данных: отсутствует ключ "d"'}
#
#         if 'sl' not in json_data['d']:
#             return {'success': False, 'error': 'Неверная структура данных: отсутствует ключ "sl"'}
#
#         # Пробуем найти вопросы в разных местах
#         groups = None
#
#         # Вариант 1: d.sl.g (как в вашем случае)
#         if 'g' in json_data['d']['sl']:
#             groups = json_data['d']['sl']['g']
#         # Вариант 2: d.g
#         elif 'g' in json_data['d']:
#             groups = json_data['d']['g']
#         # Вариант 3: d.r.g (результаты)
#         elif 'r' in json_data['d']['sl'] and 'g' in json_data['d']['sl']['r']:
#             # Это слайды с результатами, не вопросы
#             pass
#
#         if not groups:
#             return {
#                 'success': False,
#                 'error': 'В данных не найдено ни одного вопроса.',
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
#                 'error': 'В данных не найдено ни одного вопроса.',
#                 'groups': [],
#                 'total_questions': 0,
#                 'errors': result.get('errors', [])
#             }
#
#         if result['errors']:
#             result['success'] = True
#             result['partial_success'] = True
#
#         return result
#
#     except Exception as e:
#         error_msg = f"Критическая ошибка обработки JSON: {str(e)}"
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
#     """Обрабатывает данные викторины и возвращает структурированный результат"""
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
    """Удаляет HTML-теги"""
    if not html_string:
        return ""
    return re.sub(r'<[^>]+>', '', html_string).strip()


def clean_pres_info(pres_info):
    """Очищает строку presInfo от лишних символов"""
    pres_info = pres_info.strip()
    return pres_info


def process_matching_question(question):
    """Обрабатывает вопрос типа Matching (сопоставление)"""
    try:
        question_text = extract_text(question['D']['h'])

        # Получаем пары для сопоставления
        matching_data = question['C']['m']

        left_items = []
        right_items = []
        correct_pairs = []

        for pair in matching_data:
            left_text = extract_text(pair['p']['t']['h']) if 'p' in pair and 't' in pair['p'] else ''
            right_text = extract_text(pair['r']['t']['h']) if 'r' in pair and 't' in pair['r'] else ''

            left_items.append(left_text)
            right_items.append(right_text)

            # В matching правильные пары определяются по индексам
            # left_item → right_item
            correct_pairs.append(f"{left_text} → {right_text}")

        # Формируем список вариантов для отображения
        all_choices = []
        for i, left in enumerate(left_items):
            all_choices.append({
                'text': f"📌 {left} → {right_items[i] if i < len(right_items) else '...'}",
                'is_correct': True,
                'is_matching_pair': True
            })

        return {
            'text': question_text,
            'type': 'Сопоставление',
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
            'text': extract_text(question.get('D', {}).get('h', 'Вопрос на сопоставление')),
            'type': 'Сопоставление (ошибка)',
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

        # Извлекаем правильный ответ из C.na
        correct_answers = []
        if 'C' in question and 'na' in question['C']:
            for na_item in question['C']['na']:
                if 'op' in na_item:
                    # op содержит правильный ответ
                    correct_answers.append(na_item['op'])
                elif 'co' in na_item and 'op' in na_item:
                    # Другой формат
                    correct_answers.append(na_item['op'])

        # Если не нашли через na, ищем в других местах
        if not correct_answers:
            # Проверяем в D.d
            if 'D' in question and 'd' in question['D']:
                for item in question['D']['d']:
                    if isinstance(item, dict) and 'data' in item:
                        if 'v' in item['data']:
                            correct_answers.extend(item['data']['v'])

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
            'text': extract_text(question.get('D', {}).get('h', 'Числовой вопрос')),
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
    """Обрабатывает вопрос типа MultipleChoiceText (вставка текста в пропуски)"""
    try:
        question_text = extract_text(question['D']['h'])

        # Извлекаем правильные ответы из D.d
        correct_answers = []
        if 'D' in question and 'd' in question['D']:
            for item in question['D']['d']:
                if isinstance(item, dict) and 'data' in item:
                    # Для MultipleChoiceText правильные ответы в data.v
                    if 'v' in item['data']:
                        correct_answers.extend(item['data']['v'])

        return {
            'text': question_text,
            'type': 'Вставка текста',
            'type_code': 'MultipleChoiceText',
            'choices': [],
            'correct_answers': correct_answers if correct_answers else ['Нет правильных ответов'],
            'has_choices': False,
            'is_matching': False,
            'is_numeric': False,
            'error': False
        }
    except Exception as e:
        logger.error(f"Ошибка обработки MultipleChoiceText: {str(e)}")
        return {
            'text': extract_text(question.get('D', {}).get('h', 'Вопрос с пропусками')),
            'type': 'Вставка текста (ошибка)',
            'type_code': 'MultipleChoiceText',
            'choices': [],
            'correct_answers': [f'Ошибка: {str(e)[:100]}'],
            'has_choices': False,
            'is_matching': False,
            'is_numeric': False,
            'error': True
        }


def process_multiple_choice_question(question):
    """Обрабатывает вопросы с вариантами ответов (MultipleChoice, MultipleResponse)"""
    try:
        question_text = extract_text(question['D']['h'])
        q_type = question['tp']

        type_names = {
            'MultipleChoice': 'Одиночный выбор',
            'MultipleResponse': 'Множественный выбор',
            'TrueFalse': 'Верно/Неверно'
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
            'correct_answers': correct_answers if correct_answers else ['Нет правильных ответов'],
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
    """Безопасная обработка одного вопроса с перехватом ошибок"""
    try:
        q_type = question.get('tp', 'Unknown')

        # Пропускаем слайды, которые не являются вопросами
        if q_type in ['IntroSlide', 'ResultSlide', 'InfoSlide']:
            return None

        # Проверяем наличие ключа 'D'
        if 'D' not in question:
            return {
                'text': '⚠️ Ошибка: отсутствует текст вопроса',
                'type': 'Unknown',
                'type_code': q_type,
                'choices': [],
                'correct_answers': ['Ошибка в структуре вопроса'],
                'has_choices': False,
                'is_matching': False,
                'is_numeric': False,
                'error': True
            }

        # Обработка разных типов вопросов
        if q_type == 'Matching':
            return process_matching_question(question)
        elif q_type == 'MultipleChoiceText':
            return process_multiple_choice_text_question(question)
        elif q_type == 'Numeric':
            return process_numeric_question(question)
        elif q_type in ['MultipleChoice', 'MultipleResponse', 'TrueFalse']:
            return process_multiple_choice_question(question)
        else:
            # Для неизвестных типов пытаемся обработать как MultipleChoice
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
            'text': f'⚠️ Ошибка обработки вопроса {q_idx + 1}',
            'type': 'Ошибка',
            'type_code': 'Error',
            'choices': [],
            'correct_answers': [f'Ошибка: {error_msg[:100]}'],
            'has_choices': False,
            'is_matching': False,
            'is_numeric': False,
            'error': True
        }


def process_json_data(json_data):
    """Обрабатывает уже декодированный JSON"""
    result = {
        'success': True,
        'groups': [],
        'total_questions': 0,
        'errors': []
    }

    try:
        # Проверяем структуру
        if 'd' not in json_data:
            return {'success': False, 'error': 'Неверная структура данных: отсутствует ключ "d"'}

        if 'sl' not in json_data['d']:
            return {'success': False, 'error': 'Неверная структура данных: отсутствует ключ "sl"'}

        # Пробуем найти вопросы в разных местах
        groups = None

        # Вариант 1: d.sl.g (как в вашем случае)
        if 'g' in json_data['d']['sl']:
            groups = json_data['d']['sl']['g']
        # Вариант 2: d.g
        elif 'g' in json_data['d']:
            groups = json_data['d']['g']

        if not groups:
            return {
                'success': False,
                'error': 'В данных не найдено ни одного вопроса.',
                'groups': [],
                'total_questions': 0,
                'errors': [{'error': 'Группы вопросов не найдены'}]
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
                        result['errors'].append({
                            'group': group_data['name'],
                            'question_index': q_idx + 1,
                            'error': processed_question.get('correct_answers', ['Неизвестная ошибка'])[0]
                        })

                    group_data['questions'].append(processed_question)

                if group_data['questions']:
                    result['groups'].append(group_data)

            except Exception as e:
                error_msg = f"Ошибка обработки группы {group_idx + 1}: {str(e)}"
                logger.error(error_msg)
                result['errors'].append({
                    'group': group.get('T', f'Группа {group_idx + 1}'),
                    'error': error_msg
                })

        if not result['groups']:
            return {
                'success': False,
                'error': 'В данных не найдено ни одного вопроса.',
                'groups': [],
                'total_questions': 0,
                'errors': result.get('errors', [])
            }

        if result['errors']:
            result['success'] = True
            result['partial_success'] = True

        return result

    except Exception as e:
        error_msg = f"Критическая ошибка обработки JSON: {str(e)}"
        logger.error(error_msg)
        return {
            'success': False,
            'error': error_msg,
            'groups': [],
            'total_questions': 0,
            'errors': [{'error': error_msg}]
        }


def process_quiz_data(pres_info):
    """Обрабатывает данные викторины и возвращает структурированный результат"""
    try:
        pres_info = clean_pres_info(pres_info)

        # Проверяем, не является ли строка уже JSON
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
                    'errors': [{'error': str(e)}]
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
            'error': error_msg,
            'groups': [],
            'total_questions': 0,
            'errors': [{'error': error_msg}]
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