import base64
import json
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


# def decoder_func(text):
# ВСТАВЬТЕ СЮДА ВСЮ СТРОКУ presInfo (она начинается с "eNrtfWlzHMc...")
#     presInfo = f"{text}"
#     json_data =''
#     # Шаг 1: Декодируем Base64
#     try:
#         decoded = base64.b64decode(presInfo)
#         print(f"✅ Base64 декодирован. Размер: {len(decoded)} байт")
#
#         # Шаг 2: Пробуем распарсить как JSON
#         try:
#             json_data = json.loads(decoded.decode('utf-8'))
#             print("✅ Данные в формате JSON!")
#             print(json.dumps(json_data, indent=2, ensure_ascii=False)[:500])
#         except:
#             print("❌ Не JSON. Проверяем, может быть сжато...")
#
#             # Шаг 3: Пробуем распаковать GZIP
#             try:
#                 import gzip
#                 import io
#
#                 decompressed = gzip.decompress(decoded)
#                 try:
#                     json_data = json.loads(decompressed.decode('utf-8'))
#                     print("✅ Данные сжаты GZIP + JSON!")
#                     print(json.dumps(json_data, indent=2, ensure_ascii=False)[:500])
#                 except:
#                     print("Данные распакованы, но не JSON:")
#                     print(decompressed[:200])
#             except:
#                 print("❌ Не GZIP. Пробуем ZLIB...")
#
#                 # Шаг 4: Пробуем распаковать ZLIB
#                 try:
#                     decompressed = zlib.decompress(decoded)
#                     try:
#                         json_data = json.loads(decompressed.decode('utf-8'))
#                         print("✅ Данные сжаты ZLIB + JSON!")
#                         print(json.dumps(json_data, indent=2, ensure_ascii=False)[:500])
#                     except:
#                         print("Данные распакованы, но не JSON:")
#                         print(decompressed[:200])
#                 except Exception as e:
#                     print(f"❌ Не удалось распаковать: {e}")
#                     print("\nПробуем декодировать как текст (может быть бинарные данные):")
#                     try:
#                         text = decoded.decode('utf-8', errors='ignore')
#                         print(text[:500])
#                     except:
#                         print("Не удалось декодировать как текст")
#
#     except Exception as e:
#         print(f"❌ Ошибка: {e}")
#
#     import re
#     def extract_text(html_string):
#         """Удаляет HTML-теги"""
#         if not html_string:
#             return ""
#         return re.sub(r'<[^>]+>', '', html_string).strip()
#
#
#     # Получаем группы вопросов
#     groups = json_data['d']['sl']['g']
#
#     print(f"Найдено групп: {len(groups)}")
#     print("=" * 70)
#
#     for group_idx, group in enumerate(groups):
#         group_name = group.get('T', f'Группа {group_idx + 1}')
#         print(f"\n{'=' * 70}")
#         print(f"📚 ГРУППА: {group_name}")
#         print(f"{'=' * 70}")
#
#         # Получаем вопросы из группы
#         questions = group.get('S', [])
#         print(f"Вопросов в группе: {len(questions)}\n")
#
#         for q_idx, question in enumerate(questions):
#             print(f"\n{'─' * 70}")
#             print(f"❓ ВОПРОС {q_idx + 1}")
#             print(f"{'─' * 70}")
#
#             # Текст вопроса
#             question_html = question['D']['h']
#             question_text = extract_text(question_html)
#             print(f"📝 {question_text}")
#
#             # Тип вопроса
#             q_type = question['tp']
#             type_names = {
#                 'MultipleChoice': 'Одиночный выбор',
#                 'MultipleResponse': 'Множественный выбор',
#                 'TrueFalse': 'Верно/Неверно'
#             }
#             print(f"📌 Тип: {type_names.get(q_type, q_type)}")
#
#             # Получаем варианты ответов
#             choices = question['C']['chs']
#             correct_answers = []
#
#             print(f"\n📋 Варианты ответов:")
#             for choice_idx, choice in enumerate(choices, 1):
#                 choice_text = extract_text(choice['t']['h'])
#                 is_correct = choice.get('c', False)
#
#                 if is_correct:
#                     correct_answers.append(choice_text)
#                     print(f"  {choice_idx}. ✅ {choice_text} (ПРАВИЛЬНЫЙ)")
#                 else:
#                     print(f"  {choice_idx}. ❌ {choice_text}")
#
#             # Выводим правильные ответы
#             print()
#             if correct_answers:
#                 if len(correct_answers) == 1:
#                     print(f"🎯 ПРАВИЛЬНЫЙ ОТВЕТ: {correct_answers[0]}")
#                 else:
#                     print(f"🎯 ПРАВИЛЬНЫЕ ОТВЕТЫ: {', '.join(correct_answers)}")
#             else:
#                 print("⚠️ Нет правильных ответов")
#
#             print(f"{'─' * 70}")
#     #     print('-',i)
#     #     for z in i:
#     #         print('--',z)
#     #         for g in z:
#     #             print('---',g)
#     #
#     # print(json_data['d']['sl'])
#
#     # def find_quiz_data(obj, path=""):
#     #     if isinstance(obj, dict):
#     #         for key, value in obj.items():
#     #             new_path = f"{path}.{key}" if path else key
#     #             # Ищем ключи, которые могут содержать вопросы
#     #             if key in ['questions', 'quiz', 'quizData', 'items', 'answers', 'correct']:
#     #                 print(f"🔍 Найден ключ: {new_path}")
#     #                 print(f"   Содержит: {type(value)}")
#     #                 if isinstance(value, list):
#     #                     print(f"   Длина: {len(value)}")
#     #                     if len(value) > 0:
#     #                         print(f"   Пример: {str(value[0])[:300]}")
#     #                 elif isinstance(value, dict):
#     #                     print(f"   Ключи: {list(value.keys())[:10]}")
#     #                 print("-" * 60)
#     #             find_quiz_data(value, new_path)
#     #     elif isinstance(obj, list):
#     #         for i, item in enumerate(obj):
#     #             find_quiz_data(item, f"{path}[{i}]")
#     #
#     #
#     # find_quiz_data(json_data)
#     # # Рекурсивно выведем все ключи на глубину до 3 уровней
#     # def print_structure(obj, depth=0, max_depth=3):
#     #     if depth > max_depth:
#     #         return
#     #     indent = "  " * depth
#     #     if isinstance(obj, dict):
#     #         for key, value in obj.items():
#     #             print(f"{indent}{key}: {type(value).__name__}")
#     #             if isinstance(value, (dict, list)):
#     #                 print_structure(value, depth + 1, max_depth)
#     #     elif isinstance(obj, list):
#     #         if obj:
#     #             print(f"{indent}список из {len(obj)} элементов")
#     #             print_structure(obj[0], depth + 1, max_depth)
#     #
#     # print("Полная структура json_data['d']:")
# print_structure(json_data['d'])

import base64
import json
import re
from django.shortcuts import render
from django.http import JsonResponse
from zaek.forms import QuizForm


def extract_text(html_string):
    """Удаляет HTML-теги"""
    if not html_string:
        return ""
    return re.sub(r'<[^>]+>', '', html_string).strip()


def process_quiz_data(pres_info):
    """Обрабатывает данные викторины и возвращает структурированный результат"""
    try:
        # Декодируем Base64
        decoded = base64.b64decode(pres_info)
        json_data = json.loads(decoded.decode('utf-8'))

        # Получаем группы вопросов
        groups = json_data['d']['sl']['g']

        result = {
            'success': True,
            'groups': [],
            'total_questions': 0
        }

        for group in groups:
            group_data = {
                'name': group.get('T', 'Без названия'),
                'questions': []
            }

            questions = group.get('S', [])
            result['total_questions'] += len(questions)

            for question in questions:
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
                    choice_text = extract_text(choice['t']['h'])
                    is_correct = choice.get('c', False)

                    if is_correct:
                        correct_answers.append(choice_text)

                    all_choices.append({
                        'text': choice_text,
                        'is_correct': is_correct
                    })

                group_data['questions'].append({
                    'text': question_text,
                    'type': type_names.get(q_type, q_type),
                    'type_code': q_type,
                    'choices': all_choices,
                    'correct_answers': correct_answers
                })

            result['groups'].append(group_data)

        return result

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
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