# import csv
# import io
# from django.db import transaction
# from django.core.exceptions import ValidationError
# from ..models import (
#     TopicCategory,
#     ZaekProduct,
#     ZaekTopic,
#     DifficultyLevel,
#     ZaekQuestion,
#     ZaekAnswer
# )
#
#
# class CSVLoader:
#     """Загрузчик данных из CSV в базу данных"""
#
#     # Разделитель колонок
#     DELIMITER = '$'
#
#     # Допустимые типы вопросов (русские названия)
#     QUESTION_TYPES = [
#         'Выбор ответа',
#         'Множественный выбор',
#         'Текстовый ответ',
#         'Соответствие'
#     ]
#
#     # Маппинг русских названий типов на коды БД
#     TYPE_MAPPING = {
#         'Выбор ответа': 'single',
#         'Множественный выбор': 'multiple',
#         'Текстовый ответ': 'text',
#         'Соответствие': 'match',
#     }
#
#     def __init__(self, csv_file):
#         self.csv_file = csv_file
#         self.errors = []
#         self.created_count = 0
#         self.updated_count = 0
#         self.skipped_count = 0
#
#     def _clean_column_name(self, name):
#         """Очистка названия колонки от пробелов"""
#         if not name:
#             return name
#         return ' '.join(name.strip().split())
#
#     def _parse_csv(self):
#         """Парсинг CSV файла"""
#         try:
#             # Пробуем кодировки
#             for encoding in ['utf-8-sig', 'utf-8', 'cp1251']:
#                 try:
#                     self.csv_file.seek(0)
#                     content = self.csv_file.read().decode(encoding)
#                     break
#                 except UnicodeDecodeError:
#                     continue
#             else:
#                 raise ValidationError('Не удалось определить кодировку')
#
#             # Чтение CSV
#             content_io = io.StringIO(content)
#             raw_reader = csv.DictReader(
#                 content_io,
#                 delimiter=self.DELIMITER,
#                 quotechar='"',
#                 quoting=csv.QUOTE_MINIMAL
#             )
#
#             rows = []
#             for row in raw_reader:
#                 cleaned_row = {}
#                 for key, value in row.items():
#                     cleaned_key = self._clean_column_name(key)
#                     cleaned_row[cleaned_key] = value
#                 rows.append(cleaned_row)
#
#             if not rows:
#                 raise ValidationError('CSV файл пуст')
#
#             # Проверка обязательных колонок
#             required_columns = ['Тема', 'Продукт', 'Вопрос', 'Тип', 'Правильный ответ']
#             actual_columns = list(rows[0].keys())
#
#             missing_columns = []
#             for col in required_columns:
#                 if col not in actual_columns:
#                     found = False
#                     for actual in actual_columns:
#                         if actual.lower().strip() == col.lower().strip():
#                             found = True
#                             break
#                     if not found:
#                         missing_columns.append(col)
#
#             if missing_columns:
#                 raise ValidationError(
#                     f'Отсутствуют колонки: {", ".join(missing_columns)}. '
#                     f'Найдены: {", ".join(actual_columns)}'
#                 )
#
#             return rows
#
#         except Exception as e:
#             raise ValidationError(f'Ошибка при парсинге CSV: {str(e)}')
#
#
#     def _get_or_create_category(self, name):
#         if not name or not name.strip():
#             return None
#         name = name.strip()
#         category, created = TopicCategory.objects.get_or_create(name=name)
#         if created:
#             self.created_count += 1
#         return category
#
#     def _get_or_create_product(self, category, name):
#         if not name or not name.strip():
#             return None
#         name = name.strip()
#         product, created = ZaekProduct.objects.get_or_create(
#             name=name,
#             defaults={'category': category or None}
#         )
#         if created:
#             self.created_count += 1
#         elif category and product.category != category:
#             product.category = category
#             product.save()
#             self.updated_count += 1
#         return product
#
#     def _get_or_create_topic(self, name):
#         if not name or not name.strip():
#             return None
#         name = name.strip()
#         topic, created = ZaekTopic.objects.get_or_create(name=name)
#         if created:
#             self.created_count += 1
#         return topic
#
#     def _get_or_create_difficulty(self, level_value):
#         try:
#             level = int(level_value)
#         except (ValueError, TypeError):
#             if level_value and str(level_value).strip():
#                 name = str(level_value).strip()
#                 difficulty, created = DifficultyLevel.objects.get_or_create(
#                     name=name,
#                     defaults={'level': 1}
#                 )
#                 if created:
#                     self.created_count += 1
#                 return difficulty
#             return None
#
#         try:
#             return DifficultyLevel.objects.get(level=level)
#         except DifficultyLevel.DoesNotExist:
#             difficulty = DifficultyLevel.objects.create(
#                 name=f'Уровень {level}',
#                 level=level
#             )
#             self.created_count += 1
#             return difficulty
#
#     def _get_image_url(self, row):
#         possible_columns = ['URL картинки', 'Image URL', 'image_url', 'Картинка']
#         for col in possible_columns:
#             if col in row and row[col] and row[col].strip():
#                 url = row[col].strip()
#                 if url.startswith(('http://', 'https://', '/')):
#                     return url
#         return None
#
#     def _parse_options(self, options_str):
#         """Разбор вариантов ответов через |"""
#         if not options_str or not options_str.strip():
#             return []
#         return [opt.strip() for opt in options_str.split('|') if opt.strip()]
#
#     def _parse_correct_answers(self, correct_str):
#         """Разбор правильных ответов через |"""
#         if not correct_str or not correct_str.strip():
#             return []
#         return [ans.strip() for ans in correct_str.split('|') if ans.strip()]
#
#     def _get_question_type_code(self, type_name):
#         if not type_name:
#             return 'single'
#         return self.TYPE_MAPPING.get(type_name.strip(), 'single')
#
#     def _process_row(self, row):
#         """Обработка одной строки CSV"""
#         # Извлекаем данные
#         topic_name = row.get('Тема', '').strip()
#         product_name = row.get('Продукт', '').strip()
#         question_text = row.get('Вопрос', '').strip()
#         question_type_name = row.get('Тип', '').strip()
#         correct_answer_str = row.get('Правильный ответ', '').strip()
#         options_str = row.get('Варианты ответов', '').strip()
#         difficulty_level = row.get('Сложность', '').strip()
#         image_url = self._get_image_url(row)
#
#         # Валидация
#         if not question_text:
#             self.errors.append(f'Пустой вопрос')
#             self.skipped_count += 1
#             return
#
#         if question_type_name not in self.QUESTION_TYPES:
#             self.errors.append(
#                 f'Неизвестный тип "{question_type_name}" для: "{question_text[:50]}..."'
#             )
#             self.skipped_count += 1
#             return
#
#         # Для выбора ответа нужны варианты
#         if question_type_name in ['Выбор ответа', 'Множественный выбор']:
#             if not options_str:
#                 self.errors.append(f'Нет вариантов ответов для: "{question_text[:50]}..."')
#                 self.skipped_count += 1
#                 return
#             if not correct_answer_str:
#                 self.errors.append(f'Нет правильного ответа для: "{question_text[:50]}..."')
#                 self.skipped_count += 1
#                 return
#
#         try:
#             with transaction.atomic():
#                 # Получаем/создаем связанные объекты
#                 category = self._get_or_create_category('Трубы и ОРМ')
#                 product = self._get_or_create_product(category, product_name) if product_name else None
#                 topic = self._get_or_create_topic(topic_name) if topic_name else None
#                 difficulty = self._get_or_create_difficulty(difficulty_level) if difficulty_level else None
#
#                 if not difficulty:
#                     difficulty, _ = DifficultyLevel.objects.get_or_create(
#                         level=1,
#                         defaults={'name': 'Базовый', 'level': 1}
#                     )
#
#                 question_type_code = self._get_question_type_code(question_type_name)
#
#                 # Создаем вопрос
#                 question, created = ZaekQuestion.objects.get_or_create(
#                     name=question_text,
#                     defaults={
#                         'topic': topic,
#                         'difficulty': difficulty,
#                         'product': product,
#                         'image_url': image_url,
#                         'question_type': question_type_code,
#                         'comment': f'Тип: {question_type_name}',
#                     }
#                 )
#
#                 if created:
#                     self.created_count += 1
#                 else:
#                     self.updated_count += 1
#                     if topic:
#                         question.topic = topic
#                     if difficulty:
#                         question.difficulty = difficulty
#                     if product:
#                         question.product = product
#                     if image_url:
#                         question.image_url = image_url
#                     question.question_type = question_type_code
#                     question.save()
#
#                 # Удаляем старые ответы
#                 ZaekAnswer.objects.filter(question=question).delete()
#
#                 # Парсим данные
#                 options = self._parse_options(options_str)
#                 correct_answers = self._parse_correct_answers(correct_answer_str)
#
#                 # ============================================
#                 # ОСНОВНАЯ ЛОГИКА - ПРАВИЛЬНОЕ СОЗДАНИЕ ОТВЕТОВ
#                 # ============================================
#
#                 if question_type_name == 'Текстовый ответ':
#                     # Только правильный ответ
#                     ZaekAnswer.objects.create(
#                         question=question,
#                         text=correct_answer_str,
#                         is_correct=True
#                     )
#                     print(f"  📝 Текстовый ответ: {correct_answer_str}")
#
#                 elif question_type_name == 'Выбор ответа':
#                     # Все варианты - это ответы, один правильный
#                     for option in options:
#                         is_correct = (option == correct_answer_str)
#                         ZaekAnswer.objects.create(
#                             question=question,
#                             text=option,
#                             is_correct=is_correct
#                         )
#                         print(f"  {'✅' if is_correct else '❌'} {option}")
#                     print(f"  📊 Всего вариантов: {len(options)}, правильный: {correct_answer_str}")
#
#                 elif question_type_name == 'Множественный выбор':
#                     # Все варианты - это ответы, несколько правильных
#                     for option in options:
#                         is_correct = option in correct_answers
#                         ZaekAnswer.objects.create(
#                             question=question,
#                             text=option,
#                             is_correct=is_correct
#                         )
#                         print(f"  {'✅' if is_correct else '❌'} {option}")
#                     print(f"  📊 Всего вариантов: {len(options)}, правильные: {correct_answers}")
#
#                 elif question_type_name == 'Соответствие':
#                     # Для соответствия - один правильный ответ
#                     ZaekAnswer.objects.create(
#                         question=question,
#                         text=correct_answer_str,
#                         is_correct=True
#                     )
#                     if options:
#                         question.comment = f"Соответствие. Варианты: {options_str}"
#                         question.save()
#                     print(f"  🔗 Соответствие: {correct_answer_str}")
#
#                 print(f"✅ Вопрос загружен: {question_text[:50]}...")
#                 print("-" * 60)
#
#         except Exception as e:
#             self.errors.append(f'Ошибка: "{question_text[:50]}...": {str(e)}')
#             self.skipped_count += 1
#
#     def load(self):
#         """Загрузка всех данных"""
#         rows = self._parse_csv()
#         total = len(rows)
#
#         print(f"\n{'=' * 60}")
#         print(f"📥 НАЧАЛО ЗАГРУЗКИ CSV")
#         print(f"📄 Всего строк: {total}")
#         print(f"{'=' * 60}\n")
#
#         for i, row in enumerate(rows, 1):
#             print(f"\n--- Строка {i}/{total} ---")
#             self._process_row(row)
#
#         print(f"\n{'=' * 60}")
#         print(f"📊 ИТОГИ ЗАГРУЗКИ")
#         print(f"{'=' * 60}")
#         print(f"✅ Создано: {self.created_count}")
#         print(f"🔄 Обновлено: {self.updated_count}")
#         print(f"⏭️ Пропущено: {self.skipped_count}")
#         print(f"❌ Ошибок: {len(self.errors)}")
#
#         if self.errors:
#             print(f"\n❌ Ошибки:")
#             for error in self.errors:
#                 print(f"  - {error}")
#         print(f"{'=' * 60}\n")
#
#         return {
#             'total': total,
#             'created': self.created_count,
#             'updated': self.updated_count,
#             'skipped': self.skipped_count,
#             'errors': [str(error) for error in self.errors],
#         }
#
# ############################
# # import csv
# # import io
# # from django.db import transaction
# # from django.core.exceptions import ValidationError
# # from ..models import (
# #     TopicCategory,
# #     ZaekProduct,
# #     ZaekTopic,
# #     DifficultyLevel,
# #     ZaekQuestion,
# #     ZaekAnswer
# # )
# #
# #
# # class CSVLoader:
# #     COLUMN_MAPPING = {
# #         'Тема': 'topic_name',
# #         'Продукт': 'product_name',
# #         'Вопрос': 'question_text',
# #         'Тип': 'question_type',          # НОВОЕ
# #         'Правильный ответ': 'correct_answer',  # НОВОЕ
# #         'Варианты ответов': 'options',        # НОВОЕ
# #         'Сложность': 'difficulty_level',
# #         'URL картинки': 'image_url',
# #     }
# #
# #     DELIMITER = '$'
# #
# #     # Допустимые типы вопросов
# #     QUESTION_TYPES = [
# #         'Выбор ответа',
# #         'Множественный выбор',
# #         'Текстовый ответ',
# #         'Соответствие'
# #     ]
# #
# #     def __init__(self, csv_file):
# #         self.csv_file = csv_file
# #         self.errors = []
# #         self.created_count = 0
# #         self.updated_count = 0
# #         self.skipped_count = 0
# #
# #     def _parse_csv(self):
# #         """Парсинг CSV с разделителем $"""
# #         try:
# #             for encoding in ['utf-8-sig', 'utf-8', 'cp1251']:
# #                 try:
# #                     self.csv_file.seek(0)
# #                     content = self.csv_file.read().decode(encoding)
# #                     break
# #                 except UnicodeDecodeError:
# #                     continue
# #             else:
# #                 raise ValidationError('Не удалось определить кодировку.')
# #
# #             reader = csv.DictReader(
# #                 io.StringIO(content),
# #                 delimiter=self.DELIMITER,
# #                 quotechar='"',
# #                 quoting=csv.QUOTE_MINIMAL
# #             )
# #
# #             required_columns = ['Тема', 'Продукт', 'Вопрос', 'Тип', 'Правильный ответ']
# #             actual_columns = reader.fieldnames or []
# #
# #             missing_columns = [col for col in required_columns if col not in actual_columns]
# #             if missing_columns:
# #                 raise ValidationError(
# #                     f'Отсутствуют колонки: {", ".join(missing_columns)}. '
# #                     f'Найдены: {", ".join(actual_columns)}'
# #                 )
# #
# #             return list(reader)
# #
# #         except Exception as e:
# #             raise ValidationError(f'Ошибка при парсинге CSV: {str(e)}')
# #
# #     def _get_or_create_category(self, name):
# #         if not name or not name.strip():
# #             return None
# #         name = name.strip()
# #         category, created = TopicCategory.objects.get_or_create(name=name)
# #         if created:
# #             self.created_count += 1
# #         return category
# #
# #     def _get_or_create_product(self, category, name):
# #         if not name or not name.strip():
# #             return None
# #         name = name.strip()
# #         product, created = ZaekProduct.objects.get_or_create(
# #             name=name,
# #             defaults={'category': category or None}
# #         )
# #         if created:
# #             self.created_count += 1
# #         elif category and product.category != category:
# #             product.category = category
# #             product.save()
# #             self.updated_count += 1
# #         return product
# #
# #     def _get_or_create_topic(self, name):
# #         if not name or not name.strip():
# #             return None
# #         name = name.strip()
# #         topic, created = ZaekTopic.objects.get_or_create(name=name)
# #         if created:
# #             self.created_count += 1
# #         return topic
# #
# #     def _get_or_create_difficulty(self, level_value):
# #         try:
# #             level = int(level_value)
# #         except (ValueError, TypeError):
# #             if level_value and str(level_value).strip():
# #                 name = str(level_value).strip()
# #                 difficulty, created = DifficultyLevel.objects.get_or_create(
# #                     name=name,
# #                     defaults={'level': 1}
# #                 )
# #                 if created:
# #                     self.created_count += 1
# #                 return difficulty
# #             return None
# #
# #         try:
# #             return DifficultyLevel.objects.get(level=level)
# #         except DifficultyLevel.DoesNotExist:
# #             difficulty = DifficultyLevel.objects.create(
# #                 name=f'Уровень {level}',
# #                 level=level
# #             )
# #             self.created_count += 1
# #             return difficulty
# #
# #     def _get_image_url(self, row):
# #         possible_columns = ['URL картинки', 'Image URL', 'image_url', 'Картинка']
# #         for col in possible_columns:
# #             if col in row and row[col] and row[col].strip():
# #                 url = row[col].strip()
# #                 if url.startswith(('http://', 'https://', '/')):
# #                     return url
# #                 else:
# #                     self.errors.append(f'Некорректный URL: "{url}"')
# #                     return None
# #         return None
# #
# #     def _parse_options(self, options_str):
# #         """Разбор вариантов ответов, разделенных |"""
# #         if not options_str or not options_str.strip():
# #             return []
# #         # Разделяем по | и убираем пустые строки
# #         return [opt.strip() for opt in options_str.split('|') if opt.strip()]
# #
# #     def _parse_correct_answers(self, correct_str):
# #         """Разбор правильных ответов (тоже через | для множественного выбора)"""
# #         if not correct_str or not correct_str.strip():
# #             return []
# #         return [ans.strip() for ans in correct_str.split('|') if ans.strip()]
# #
# #     def _process_row(self, row):
# #         """Обработка одной строки CSV"""
# #         # Базовые поля
# #         topic_name = row.get('Тема', '').strip()
# #         product_name = row.get('Продукт', '').strip()
# #         question_text = row.get('Вопрос', '').strip()
# #         question_type = row.get('Тип', '').strip()
# #         correct_answer_str = row.get('Правильный ответ', '').strip()
# #         options_str = row.get('Варианты ответов', '').strip()
# #         difficulty_level = row.get('Сложность', '').strip()
# #         image_url = self._get_image_url(row)
# #
# #         # Валидация
# #         if not question_text:
# #             self.errors.append(f'Пустой вопрос в строке: {row}')
# #             self.skipped_count += 1
# #             return
# #
# #         if question_type not in self.QUESTION_TYPES:
# #             self.errors.append(
# #                 f'Неизвестный тип вопроса "{question_type}" для: "{question_text[:50]}...". '
# #                 f'Допустимые: {", ".join(self.QUESTION_TYPES)}'
# #             )
# #             self.skipped_count += 1
# #             return
# #
# #         # Для текстового ответа варианты не нужны
# #         if question_type == 'Текстовый ответ' and not correct_answer_str:
# #             self.errors.append(f'Для текстового ответа нужен правильный ответ: "{question_text[:50]}..."')
# #             self.skipped_count += 1
# #             return
# #
# #         # Для выбора ответа нужны варианты
# #         if question_type in ['Выбор ответа', 'Множественный выбор'] and not options_str:
# #             self.errors.append(f'Для типа "{question_type}" нужны варианты ответов: "{question_text[:50]}..."')
# #             self.skipped_count += 1
# #             return
# #
# #         try:
# #             with transaction.atomic():
# #                 # Создаем/получаем связанные объекты
# #                 category = self._get_or_create_category('Трубы и ОРМ')  # Можно брать из CSV
# #                 product = self._get_or_create_product(category, product_name) if product_name else None
# #                 topic = self._get_or_create_topic(topic_name) if topic_name else None
# #                 difficulty = self._get_or_create_difficulty(difficulty_level) if difficulty_level else None
# #
# #                 if not difficulty:
# #                     difficulty, _ = DifficultyLevel.objects.get_or_create(
# #                         level=1,
# #                         defaults={'name': 'Базовый', 'level': 1}
# #                     )
# #                     if _:
# #                         self.created_count += 1
# #
# #                 # Создаем или обновляем вопрос
# #                 question, created = ZaekQuestion.objects.get_or_create(
# #                     name=question_text,
# #                     defaults={
# #                         'topic': topic,
# #                         'difficulty': difficulty,
# #                         'product': product,
# #                         'image_url': image_url,
# #                         'comment': f'Тип: {question_type}',
# #                     }
# #                 )
# #
# #                 if created:
# #                     self.created_count += 1
# #                 else:
# #                     self.updated_count += 1
# #                     if topic:
# #                         question.topic = topic
# #                     if difficulty:
# #                         question.difficulty = difficulty
# #                     if product:
# #                         question.product = product
# #                     if image_url:
# #                         question.image_url = image_url
# #                     question.save()
# #
# #                 # --- ГЛАВНОЕ: УДАЛЯЕМ СТАРЫЕ ОТВЕТЫ И СОЗДАЕМ НОВЫЕ ---
# #                 ZaekAnswer.objects.filter(question=question).delete()
# #
# #                 # Парсим варианты и правильные ответы
# #                 options = self._parse_options(options_str)
# #                 correct_answers = self._parse_correct_answers(correct_answer_str)
# #
# #                 if question_type == 'Текстовый ответ':
# #                     # Только один правильный ответ (текстовый)
# #                     ZaekAnswer.objects.create(
# #                         question=question,
# #                         text=correct_answer_str,
# #                         is_correct=True
# #                     )
# #
# #                 elif question_type == 'Выбор ответа':
# #                     # Один правильный, остальные неправильные
# #                     for option in options:
# #                         is_correct = (option == correct_answer_str)
# #                         ZaekAnswer.objects.create(
# #                             question=question,
# #                             text=option,
# #                             is_correct=is_correct
# #                         )
# #
# #                 elif question_type == 'Множественный выбор':
# #                     # Несколько правильных
# #                     for option in options:
# #                         is_correct = option in correct_answers
# #                         ZaekAnswer.objects.create(
# #                             question=question,
# #                             text=option,
# #                             is_correct=is_correct
# #                         )
# #
# #                 elif question_type == 'Соответствие':
# #                     # Для соответствия нужна особая логика
# #                     # Пока сохраняем как текстовый ответ с правильным вариантом
# #                     ZaekAnswer.objects.create(
# #                         question=question,
# #                         text=correct_answer_str,
# #                         is_correct=True
# #                     )
# #                     # Дополнительно можно сохранить варианты как комментарий
# #                     if options:
# #                         question.comment = f"Соответствие. Варианты: {options_str}"
# #                         question.save()
# #
# #         except Exception as e:
# #             self.errors.append(f'Ошибка при обработке "{question_text[:50]}...": {str(e)}')
# #             self.skipped_count += 1
# #
# #     def load(self):
# #         """Загрузка всех данных"""
# #         rows = self._parse_csv()
# #         total = len(rows)
# #
# #         for i, row in enumerate(rows, 1):
# #             self._process_row(row)
# #
# #         return {
# #             'total': total,
# #             'created': self.created_count,
# #             'updated': self.updated_count,
# #             'skipped': self.skipped_count,
# #             'errors': [str(error) for error in self.errors],
# #         }
# #
# #
# # #######################
# # # import csv
# # # import io
# # # from django.db import transaction
# # # from django.core.exceptions import ValidationError
# # # from ..models import (
# # #     TopicCategory,
# # #     ZaekProduct,
# # #     ZaekTopic,
# # #     DifficultyLevel,
# # #     ZaekQuestion,
# # #     ZaekAnswer
# # # )
# # #
# # #
# # # class CSVLoader:
# # #     """Класс для загрузки данных из CSV в базу данных"""
# # #
# # #     # Маппинг колонок из CSV на поля моделей
# # #     COLUMN_MAPPING = {
# # #         'Название категории': 'category_name',
# # #         'Продукт': 'product_name',
# # #         'Вопрос': 'question_text',
# # #         'Ответ': 'answer_text',
# # #         'Тема вопроса': 'topic_name',
# # #         'Уровень сложности': 'difficulty_level',
# # #         'Ссылка на изображение': 'image_url',  # НОВАЯ КОЛОНКА
# # #         'Image URL': 'image_url',  # Альтернативное название
# # #         'image_url': 'image_url',  # Альтернативное название
# # #     }
# # #
# # #     # Разделитель колонок
# # #     DELIMITER = '$'
# # #
# # #     def __init__(self, csv_file):
# # #         self.csv_file = csv_file
# # #         self.errors = []
# # #         self.created_count = 0
# # #         self.updated_count = 0
# # #         self.skipped_count = 0
# # #
# # #     def _parse_csv(self):
# # #         """Парсит CSV файл и возвращает список словарей"""
# # #         try:
# # #             # Пробуем разные кодировки
# # #             for encoding in ['utf-8-sig', 'utf-8', 'cp1251']:
# # #                 try:
# # #                     self.csv_file.seek(0)
# # #                     content = self.csv_file.read().decode(encoding)
# # #                     break
# # #                 except UnicodeDecodeError:
# # #                     continue
# # #             else:
# # #                 raise ValidationError('Не удалось определить кодировку файла. Используйте UTF-8 или Windows-1251.')
# # #
# # #             # Парсим CSV с разделителем $
# # #             reader = csv.DictReader(
# # #                 io.StringIO(content),
# # #                 delimiter=self.DELIMITER,
# # #                 quotechar='"',
# # #                 quoting=csv.QUOTE_MINIMAL
# # #             )
# # #
# # #             # Проверяем наличие необходимых колонок
# # #             required_columns = ['Название категории', 'Продукт', 'Вопрос', 'Ответ']
# # #             actual_columns = reader.fieldnames or []
# # #
# # #             missing_columns = [col for col in required_columns if col not in actual_columns]
# # #             if missing_columns:
# # #                 raise ValidationError(
# # #                     f'В файле отсутствуют обязательные колонки: {", ".join(missing_columns)}. '
# # #                     f'Доступны: {", ".join(actual_columns)}'
# # #                 )
# # #
# # #             return list(reader)
# # #
# # #         except Exception as e:
# # #             raise ValidationError(f'Ошибка при парсинге CSV: {str(e)}')
# # #
# # #     def _get_or_create_category(self, name):
# # #         """Получает или создает категорию"""
# # #         if not name or not name.strip():
# # #             return None
# # #
# # #         name = name.strip()
# # #         category, created = TopicCategory.objects.get_or_create(
# # #             name=name,
# # #             defaults={'name': name}
# # #         )
# # #         if created:
# # #             self.created_count += 1
# # #         return category
# # #
# # #     def _get_or_create_product(self, category, name):
# # #         """Получает или создает продукт"""
# # #         if not name or not name.strip():
# # #             return None
# # #
# # #         name = name.strip()
# # #         product, created = ZaekProduct.objects.get_or_create(
# # #             name=name,
# # #             defaults={
# # #                 'category': category,
# # #                 'name': name,
# # #             }
# # #         )
# # #         if created:
# # #             self.created_count += 1
# # #         elif category and product.category != category:
# # #             # Обновляем категорию у существующего продукта
# # #             product.category = category
# # #             product.save()
# # #             self.updated_count += 1
# # #         return product
# # #
# # #     def _get_or_create_topic(self, name):
# # #         """Получает или создает тему вопроса"""
# # #         if not name or not name.strip():
# # #             return None
# # #
# # #         name = name.strip()
# # #         topic, created = ZaekTopic.objects.get_or_create(
# # #             name=name,
# # #             defaults={'name': name}
# # #         )
# # #         if created:
# # #             self.created_count += 1
# # #         return topic
# # #
# # #     def _get_or_create_difficulty(self, level_value):
# # #         """Получает или создает уровень сложности"""
# # #         try:
# # #             level = int(level_value)
# # #         except (ValueError, TypeError):
# # #             # Если не число, пробуем найти по имени
# # #             if level_value and str(level_value).strip():
# # #                 name = str(level_value).strip()
# # #                 difficulty, created = DifficultyLevel.objects.get_or_create(
# # #                     name=name,
# # #                     defaults={'level': 1, 'name': name}
# # #                 )
# # #                 if created:
# # #                     self.created_count += 1
# # #                 return difficulty
# # #             return None
# # #
# # #         # Ищем по уровню
# # #         try:
# # #             difficulty = DifficultyLevel.objects.get(level=level)
# # #             return difficulty
# # #         except DifficultyLevel.DoesNotExist:
# # #             # Создаем новый уровень
# # #             name = f'Уровень {level}'
# # #             difficulty = DifficultyLevel.objects.create(
# # #                 name=name,
# # #                 level=level
# # #             )
# # #             self.created_count += 1
# # #             return difficulty
# # #
# # #     def _get_image_url(self, row):
# # #         """
# # #         Извлекает URL изображения из строки CSV.
# # #         Проверяет несколько возможных названий колонок.
# # #         """
# # #         # Возможные названия колонок для изображения
# # #         possible_columns = ['Ссылка на изображение', 'Image URL', 'image_url', 'Картинка', 'Изображение']
# # #
# # #         for col in possible_columns:
# # #             if col in row and row[col] and row[col].strip():
# # #                 url = row[col].strip()
# # #                 # Простая валидация URL
# # #                 if url.startswith(('http://', 'https://', '/')):
# # #                     return url
# # #                 else:
# # #                     self.errors.append(f'Неверный формат URL: "{url}"')
# # #                     return None
# # #
# # #         return None
# # #
# # #     def _process_row(self, row):
# # #         """Обрабатывает одну строку CSV"""
# # #         # Извлекаем данные из строки
# # #         category_name = row.get('Название категории', '').strip()
# # #         product_name = row.get('Продукт', '').strip()
# # #         question_text = row.get('Вопрос', '').strip()
# # #         answer_text = row.get('Ответ', '').strip()
# # #         topic_name = row.get('Тема вопроса', '').strip()
# # #         difficulty_level = row.get('Уровень сложности', '').strip()
# # #         image_url = self._get_image_url(row)  # НОВОЕ: извлекаем URL изображения
# # #
# # #         # Проверяем обязательные поля
# # #         if not question_text:
# # #             self.errors.append(f'Пропущен вопрос в строке: {row}')
# # #             self.skipped_count += 1
# # #             return
# # #
# # #         if not answer_text:
# # #             self.errors.append(f'Пропущен ответ для вопроса: "{question_text[:50]}..."')
# # #             self.skipped_count += 1
# # #             return
# # #
# # #         try:
# # #             with transaction.atomic():
# # #                 # Получаем или создаем связанные объекты
# # #                 category = self._get_or_create_category(category_name) if category_name else None
# # #                 product = self._get_or_create_product(category, product_name) if product_name else None
# # #                 topic = self._get_or_create_topic(topic_name) if topic_name else None
# # #                 difficulty = self._get_or_create_difficulty(difficulty_level) if difficulty_level else None
# # #
# # #                 # Если нет уровня сложности, используем уровень 1
# # #                 if not difficulty:
# # #                     difficulty, _ = DifficultyLevel.objects.get_or_create(
# # #                         level=1,
# # #                         defaults={'name': 'Базовый', 'level': 1}
# # #                     )
# # #                     if _:
# # #                         self.created_count += 1
# # #
# # #                 # Ищем существующий вопрос по тексту
# # #                 question, created = ZaekQuestion.objects.get_or_create(
# # #                     name=question_text,
# # #                     defaults={
# # #                         'topic': topic,
# # #                         'difficulty': difficulty,
# # #                         'product': product,
# # #                         'image_url': image_url,  # НОВОЕ: добавляем при создании
# # #                         'comment': f'Загружен из CSV. Категория: {category_name}',
# # #                     }
# # #                 )
# # #
# # #                 if created:
# # #                     self.created_count += 1
# # #                 else:
# # #                     # Обновляем существующий вопрос
# # #                     self.updated_count += 1
# # #                     if topic:
# # #                         question.topic = topic
# # #                     if difficulty:
# # #                         question.difficulty = difficulty
# # #                     if product:
# # #                         question.product = product
# # #                     # НОВОЕ: обновляем image_url, если он передан и не пустой
# # #                     if image_url:
# # #                         question.image_url = image_url
# # #                     question.save()
# # #
# # #                 # Обновляем ответы: удаляем старые правильные ответы и создаем новый
# # #                 # (поскольку по условию только один правильный ответ)
# # #                 ZaekAnswer.objects.filter(
# # #                     question=question,
# # #                     is_correct=True
# # #                 ).delete()
# # #
# # #                 # Создаем новый правильный ответ
# # #                 ZaekAnswer.objects.create(
# # #                     question=question,
# # #                     text=answer_text,
# # #                     is_correct=True
# # #                 )
# # #
# # #         except Exception as e:
# # #             self.errors.append(f'Ошибка при обработке вопроса "{question_text[:50]}...": {str(e)}')
# # #             self.skipped_count += 1
# # #
# # #     def load(self):
# # #         """Основной метод загрузки данных"""
# # #         rows = self._parse_csv()
# # #
# # #         total = len(rows)
# # #         for i, row in enumerate(rows, 1):
# # #             self._process_row(row)
# # #
# # #         return {
# # #             'total': total,
# # #             'created': self.created_count,
# # #             'updated': self.updated_count,
# # #             'skipped': self.skipped_count,
# # #              'errors': [str(error) for error in self.errors],
# # #         }
# # #
# # # # zaek/utils/csv_loader.py
# # # # import csv
# # # # import io
# # # # from django.db import transaction
# # # # from django.core.exceptions import ValidationError
# # # # from ..models import (
# # # #     TopicCategory,
# # # #     ZaekProduct,
# # # #     ZaekTopic,
# # # #     DifficultyLevel,
# # # #     ZaekQuestion,
# # # #     ZaekAnswer
# # # # )
# # # # import logging
# # # # import re
# # # #
# # # # logger = logging.getLogger(__name__)
# # # #
# # # #
# # # # class CSVLoader:
# # # #     """Класс для загрузки данных из CSV в базу данных"""
# # # #
# # # #     # Разделитель колонок
# # # #     DELIMITER = '$'
# # # #
# # # #     def __init__(self, csv_file, encoding='utf-8'):
# # # #         self.csv_file = csv_file
# # # #         self.encoding = encoding
# # # #         self.errors = []
# # # #         self.created_count = 0
# # # #         self.updated_count = 0
# # # #         self.skipped_count = 0
# # # #         self.total_count = 0
# # # #
# # # #     def _detect_encoding(self):
# # # #         """Определяет кодировку файла"""
# # # #         encodings = ['utf-8-sig', 'utf-8', 'cp1251', 'windows-1251', 'latin-1']
# # # #
# # # #         for encoding in encodings:
# # # #             try:
# # # #                 self.csv_file.seek(0)
# # # #                 content = self.csv_file.read().decode(encoding)
# # # #                 self.csv_file.seek(0)
# # # #                 return encoding, content
# # # #             except UnicodeDecodeError:
# # # #                 continue
# # # #
# # # #         raise ValidationError('Не удалось определить кодировку файла. Используйте UTF-8 или Windows-1251.')
# # # #
# # # #     def _normalize_column_name(self, col_name):
# # # #         """Нормализует название колонки"""
# # # #         col_name = col_name.strip().lower()
# # # #         # Убираем лишние пробелы и специальные символы
# # # #         col_name = re.sub(r'[^\w\s]', '', col_name)
# # # #         col_name = re.sub(r'\s+', ' ', col_name).strip()
# # # #         return col_name
# # # #
# # # #     def _parse_csv(self):
# # # #         """Парсит CSV файл и возвращает список строк"""
# # # #         try:
# # # #             # Определяем кодировку
# # # #             encoding, content = self._detect_encoding()
# # # #
# # # #             # Читаем CSV с разделителем $
# # # #             reader = csv.DictReader(
# # # #                 io.StringIO(content),
# # # #                 delimiter=self.DELIMITER,
# # # #                 quotechar='"',
# # # #                 quoting=csv.QUOTE_MINIMAL
# # # #             )
# # # #
# # # #             # Получаем заголовки
# # # #             actual_columns = reader.fieldnames or []
# # # #
# # # #             # Создаем маппинг колонок
# # # #             column_mapping = {}
# # # #
# # # #             # Определяем соответствие колонок по ключевым словам
# # # #             for col in actual_columns:
# # # #                 col_normalized = self._normalize_column_name(col)
# # # #
# # # #                 # Категория
# # # #                 if any(keyword in col_normalized for keyword in ['категория', 'название категории']):
# # # #                     column_mapping['category'] = col
# # # #                 # Продукт
# # # #                 elif any(keyword in col_normalized for keyword in ['продукт']):
# # # #                     column_mapping['product'] = col
# # # #                 # Вопрос
# # # #                 elif any(keyword in col_normalized for keyword in ['вопрос']):
# # # #                     column_mapping['question'] = col
# # # #                 # Ответ
# # # #                 elif any(keyword in col_normalized for keyword in ['ответ']):
# # # #                     column_mapping['answer'] = col
# # # #                 # Тема
# # # #                 elif any(keyword in col_normalized for keyword in ['тема']):
# # # #                     column_mapping['topic'] = col
# # # #                 # Уровень сложности
# # # #                 elif any(keyword in col_normalized for keyword in ['уровень', 'сложности']):
# # # #                     column_mapping['difficulty'] = col
# # # #                 # Изображение
# # # #                 elif any(keyword in col_normalized for keyword in ['изображение', 'image', 'ссылка', 'url']):
# # # #                     column_mapping['image_url'] = col
# # # #
# # # #             # Проверяем наличие обязательных колонок
# # # #             required = ['category', 'product', 'question', 'answer']
# # # #             missing = [r for r in required if r not in column_mapping]
# # # #
# # # #             if missing:
# # # #                 raise ValidationError(
# # # #                     f'В файле отсутствуют обязательные колонки. '
# # # #                     f'Найдены колонки: {", ".join(actual_columns)}. '
# # # #                     f'Ожидаются: категория, продукт, вопрос, ответ'
# # # #                 )
# # # #
# # # #             # Преобразуем строки в словари
# # # #             rows = []
# # # #             for row_num, row in enumerate(reader, start=2):
# # # #                 normalized_row = {}
# # # #                 for key, value in row.items():
# # # #                     normalized_row[key.strip()] = value.strip() if value else ''
# # # #                 rows.append(normalized_row)
# # # #
# # # #             self.total_count = len(rows)
# # # #             logger.info(f'Найдено {self.total_count} строк в CSV')
# # # #             logger.info(f'Колонки: {actual_columns}')
# # # #             logger.info(f'Маппинг: {column_mapping}')
# # # #
# # # #             return rows, column_mapping
# # # #
# # # #         except Exception as e:
# # # #             raise ValidationError(f'Ошибка при чтении CSV: {str(e)}')
# # # #
# # # #     def _get_or_create_category(self, name):
# # # #         """Получает или создает категорию"""
# # # #         if not name or not name.strip():
# # # #             return None
# # # #
# # # #         name = name.strip()
# # # #         category, created = TopicCategory.objects.get_or_create(
# # # #             name=name
# # # #         )
# # # #         if created:
# # # #             self.created_count += 1
# # # #             logger.info(f'Создана категория: {name}')
# # # #         return category
# # # #
# # # #     def _get_or_create_product(self, category, name):
# # # #         """Получает или создает продукт"""
# # # #         if not name or not name.strip():
# # # #             return None
# # # #
# # # #         name = name.strip()
# # # #         product, created = ZaekProduct.objects.get_or_create(
# # # #             name=name,
# # # #             defaults={'category': category} if category else {}
# # # #         )
# # # #         if created:
# # # #             self.created_count += 1
# # # #             logger.info(f'Создан продукт: {name}')
# # # #         elif category and product.category != category:
# # # #             product.category = category
# # # #             product.save()
# # # #             self.updated_count += 1
# # # #         return product
# # # #
# # # #     def _get_or_create_topic(self, name):
# # # #         """Получает или создает тему"""
# # # #         if not name or not name.strip():
# # # #             return None
# # # #
# # # #         name = name.strip()
# # # #         topic, created = ZaekTopic.objects.get_or_create(
# # # #             name=name
# # # #         )
# # # #         if created:
# # # #             self.created_count += 1
# # # #             logger.info(f'Создана тема: {name}')
# # # #         return topic
# # # #
# # # #     def _get_or_create_difficulty(self, level_value):
# # # #         """Получает или создает уровень сложности"""
# # # #         if not level_value or not str(level_value).strip():
# # # #             return None
# # # #
# # # #         level_str = str(level_value).strip()
# # # #
# # # #         # Пробуем получить число
# # # #         try:
# # # #             level = int(level_str)
# # # #         except (ValueError, TypeError):
# # # #             # Если не число, ищем по имени
# # # #             difficulty, created = DifficultyLevel.objects.get_or_create(
# # # #                 name=level_str,
# # # #                 defaults={'level': 1}
# # # #             )
# # # #             if created:
# # # #                 self.created_count += 1
# # # #             return difficulty
# # # #
# # # #         # Ищем по уровню
# # # #         difficulty, created = DifficultyLevel.objects.get_or_create(
# # # #             level=level,
# # # #             defaults={'name': f'Уровень {level}'}
# # # #         )
# # # #         if created:
# # # #             self.created_count += 1
# # # #         return difficulty
# # # #
# # # #     def _get_image_url(self, row, column_mapping):
# # # #         """Извлекает URL изображения из строки"""
# # # #         image_col = column_mapping.get('image_url')
# # # #         if image_col and image_col in row:
# # # #             url = row[image_col]
# # # #             if url and url.strip():
# # # #                 url = url.strip()
# # # #                 # Проверяем, что это валидный URL
# # # #                 if url.startswith(('http://', 'https://', '/')):
# # # #                     return url
# # # #                 else:
# # # #                     self.errors.append(f'Неверный URL изображения: "{url}"')
# # # #                     return None
# # # #         return None
# # # #
# # # #     def _process_row(self, row, column_mapping):
# # # #         """Обрабатывает одну строку CSV"""
# # # #         try:
# # # #             # Получаем значения из строки
# # # #             category_name = row.get(column_mapping.get('category', ''), '').strip()
# # # #             product_name = row.get(column_mapping.get('product', ''), '').strip()
# # # #             question_text = row.get(column_mapping.get('question', ''), '').strip()
# # # #             answer_text = row.get(column_mapping.get('answer', ''), '').strip()
# # # #             topic_name = row.get(column_mapping.get('topic', ''), '').strip() if 'topic' in column_mapping else ''
# # # #             difficulty_level = row.get(column_mapping.get('difficulty', ''),
# # # #                                        '').strip() if 'difficulty' in column_mapping else '1'
# # # #             image_url = self._get_image_url(row, column_mapping)
# # # #
# # # #             # Проверяем обязательные поля
# # # #             if not question_text:
# # # #                 self.errors.append(f'Пропущен вопрос в строке: {row}')
# # # #                 self.skipped_count += 1
# # # #                 return
# # # #
# # # #             if not answer_text:
# # # #                 self.errors.append(f'Пропущен ответ для вопроса: "{question_text[:50]}..."')
# # # #                 self.skipped_count += 1
# # # #                 return
# # # #
# # # #             with transaction.atomic():
# # # #                 # Создаем или получаем связанные объекты
# # # #                 category = self._get_or_create_category(category_name) if category_name else None
# # # #                 product = self._get_or_create_product(category, product_name) if product_name else None
# # # #                 topic = self._get_or_create_topic(topic_name) if topic_name else None
# # # #                 difficulty = self._get_or_create_difficulty(difficulty_level) if difficulty_level else None
# # # #
# # # #                 # Если уровень сложности не указан, используем уровень 1
# # # #                 if not difficulty:
# # # #                     difficulty, _ = DifficultyLevel.objects.get_or_create(
# # # #                         level=1,
# # # #                         defaults={'name': 'Простой'}
# # # #                     )
# # # #
# # # #                 # Создаем или обновляем вопрос
# # # #                 question, created = ZaekQuestion.objects.get_or_create(
# # # #                     name=question_text,
# # # #                     defaults={
# # # #                         'topic': topic,
# # # #                         'difficulty': difficulty,
# # # #                         'product': product,
# # # #                         'image_url': image_url or '',
# # # #                         'comment': f'Загружено из CSV. Категория: {category_name}'
# # # #                     }
# # # #                 )
# # # #
# # # #                 if created:
# # # #                     self.created_count += 1
# # # #                     logger.info(f'Создан вопрос: {question_text[:50]}...')
# # # #                 else:
# # # #                     # Обновляем существующий вопрос
# # # #                     self.updated_count += 1
# # # #                     if topic:
# # # #                         question.topic = topic
# # # #                     if difficulty:
# # # #                         question.difficulty = difficulty
# # # #                     if product:
# # # #                         question.product = product
# # # #                     if image_url:
# # # #                         question.image_url = image_url
# # # #                     question.save()
# # # #                     logger.info(f'Обновлен вопрос: {question_text[:50]}...')
# # # #
# # # #                 # Удаляем старые ответы для этого вопроса
# # # #                 ZaekAnswer.objects.filter(question=question).delete()
# # # #
# # # #                 # Разбиваем ответы, если их несколько (разделитель ;)
# # # #                 if ';' in answer_text:
# # # #                     answers = [a.strip() for a in answer_text.split(';') if a.strip()]
# # # #                 else:
# # # #                     answers = [answer_text]
# # # #
# # # #                 # Создаем ответы (первый - правильный, остальные - неправильные)
# # # #                 for i, ans in enumerate(answers):
# # # #                     ZaekAnswer.objects.create(
# # # #                         question=question,
# # # #                         text=ans,
# # # #                         is_correct=(i == 0)  # Первый ответ - правильный
# # # #                     )
# # # #
# # # #                 logger.info(f'Создано {len(answers)} ответов для вопроса: {question_text[:30]}...')
# # # #
# # # #         except Exception as e:
# # # #             error_msg = f'Ошибка при обработке строки: {str(e)}'
# # # #             self.errors.append(error_msg)
# # # #             self.skipped_count += 1
# # # #             logger.error(error_msg)
# # # #
# # # #     def load(self):
# # # #         """Загружает данные из CSV файла"""
# # # #         try:
# # # #             # Парсим CSV
# # # #             rows, column_mapping = self._parse_csv()
# # # #
# # # #             if not rows:
# # # #                 self.errors.append('Файл пуст или не содержит данных')
# # # #                 return self.get_results()
# # # #
# # # #             logger.info(f'Найдено {len(rows)} строк для обработки')
# # # #
# # # #             # Обрабатываем каждую строку
# # # #             for i, row in enumerate(rows, 1):
# # # #                 self._process_row(row, column_mapping)
# # # #
# # # #             return self.get_results()
# # # #
# # # #         except ValidationError as e:
# # # #             self.errors.append(str(e))
# # # #             return self.get_results()
# # # #         except Exception as e:
# # # #             self.errors.append(f'Критическая ошибка: {str(e)}')
# # # #             logger.error(f'Критическая ошибка при загрузке CSV: {str(e)}')
# # # #             return self.get_results()
# # # #
# # # #     def get_results(self):
# # # #         """Возвращает результаты загрузки"""
# # # #         return {
# # # #             'total': self.total_count,
# # # #             'created': self.created_count,
# # # #             'updated': self.updated_count,
# # # #             'skipped': self.skipped_count,
# # # #             'errors': self.errors,
# # # #         }



import csv
import json
import logging
from django.db import transaction
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from io import TextIOWrapper

from zaek.models import (
    TopicCategory,
    ZaekProduct,
    ZaekTopic,
    DifficultyLevel,
    ZaekQuestion,
    ZaekAnswer
)

logger = logging.getLogger(__name__)


class CSVLoader:
    """Загрузка данных из CSV в базу данных"""

    # Разделитель колонок
    DELIMITER = '$'  # Изменено с ';' на '$' как в вашем CSV

    # Допустимые типы вопросов (русские названия)
    QUESTION_TYPES = [
        'Выбор ответа',
        'Множественный выбор',
        'Текстовый ответ',
        'Соответствие'
    ]

    # Соответствие русских названий типам в БД
    TYPE_MAPPING = {
        'Выбор ответа': 'single',
        'Множественный выбор': 'multiple',
        'Текстовый ответ': 'text',
        'Соответствие': 'match'
    }

    # Обязательные колонки в CSV
    REQUIRED_COLUMNS = [
        '№',
        'Название категории',
        'Продукт',
        'Название уровня',
        'Вопрос',
        'Тема ответа',
        'Правильный ответ',
        'Варианты ответов'
    ]

    def __init__(self, csv_file):
        """
        Инициализация загрузчика

        Args:
            csv_file: файл CSV (путь или UploadedFile)
        """
        self.csv_file = csv_file
        self.stats = {
            'total_rows': 0,
            'success': 0,
            'errors': 0,
            'error_messages': [],
            'created_questions': [],
            'skipped_rows': 0
        }

    def load(self):
        """Основной метод загрузки данных"""
        try:
            # Определяем тип файла и открываем его
            if isinstance(self.csv_file, UploadedFile):
                # Если загруженный файл
                csv_data = TextIOWrapper(self.csv_file.file, encoding='utf-8-sig')
            elif isinstance(self.csv_file, str):
                # Если путь к файлу
                csv_data = open(self.csv_file, 'r', encoding='utf-8-sig')
            else:
                raise ValueError('Неподдерживаемый тип файла')

            reader = csv.DictReader(csv_data, delimiter=self.DELIMITER)

            # Проверяем наличие обязательных колонок
            self._validate_columns(reader.fieldnames)

            # Получаем или создаем уровни сложности
            difficulty_levels = self._get_difficulty_levels()

            # Обрабатываем строки
            for row_num, row in enumerate(reader, start=2):
                self.stats['total_rows'] += 1

                try:
                    with transaction.atomic():
                        question = self._process_row(row, difficulty_levels)
                        self.stats['success'] += 1
                        self.stats['created_questions'].append({
                            'row': row_num,
                            'question': question.name[:50],
                            'id': question.id
                        })
                except Exception as e:
                    self.stats['errors'] += 1
                    error_msg = f'Строка {row_num}: {str(e)}'
                    self.stats['error_messages'].append(error_msg)
                    logger.error(f'Ошибка импорта: {error_msg}')
                    # Не прерываем импорт при ошибке в одной строке

            # Закрываем файл если это путь
            if isinstance(self.csv_file, str):
                csv_data.close()

            return self.stats

        except Exception as e:
            logger.error(f'Критическая ошибка загрузки: {str(e)}')
            raise

    def _validate_columns(self, fieldnames):
        """Проверка наличия обязательных колонок"""
        missing = [col for col in self.REQUIRED_COLUMNS if col not in fieldnames]
        if missing:
            raise ValueError(
                f'Отсутствуют обязательные колонки: {", ".join(missing)}\n'
                f'Доступные колонки: {", ".join(fieldnames)}'
            )

    def _get_difficulty_levels(self):
        """Получение или создание уровней сложности"""
        levels_data = [
            {'name': 'Базовый', 'level': 1},
            {'name': 'Средний', 'level': 2},
            {'name': 'Продвинутый', 'level': 3},
        ]

        levels = {}
        for data in levels_data:
            level, created = DifficultyLevel.objects.get_or_create(
                level=data['level'],
                defaults={'name': data['name']}
            )
            levels[data['level']] = level

            if created:
                logger.info(f'Создан уровень сложности: {data["name"]}')

        return levels

    def _process_row(self, row, difficulty_levels):
        """Обработка одной строки CSV"""
        # 1. Получаем или создаем категорию
        category_name = row.get('Название категории', '').strip()
        if category_name:
            category, created = TopicCategory.objects.get_or_create(
                name=category_name
            )
            if created:
                logger.info(f'Создана категория: {category_name}')
        else:
            category = None
            logger.warning('Пропущена категория в строке')

        # 2. Получаем или создаем тему
        topic_name = row.get('Тема ответа', '').strip()
        if not topic_name:
            topic_name = 'Тест DKC'  # Значение по умолчанию

        topic, created = ZaekTopic.objects.get_or_create(
            name=topic_name
        )
        if created:
            logger.info(f'Создана тема: {topic_name}')

        # 3. Получаем или создаем продукт
        product_name = row.get('Продукт', '').strip()
        product = None
        if product_name and category:
            product, created = ZaekProduct.objects.get_or_create(
                name=product_name,
                defaults={'category': category}
            )
            if created:
                logger.info(f'Создан продукт: {product_name} в категории {category_name}')

        # 4. Определяем уровень сложности
        level_str = row.get('Название уровня', '1')
        level_num = 1  # По умолчанию
        if '1' in level_str:
            level_num = 1
        elif '2' in level_str:
            level_num = 2
        elif '3' in level_str:
            level_num = 3

        difficulty = difficulty_levels.get(level_num, difficulty_levels[1])

        # 5. Определяем тип вопроса
        question_text = row.get('Вопрос', '').strip()
        if not question_text:
            raise ValueError('Вопрос не может быть пустым')

        options_str = row.get('Варианты ответов', '')
        correct_answer = row.get('Правильный ответ', '').strip()

        question_type = self._determine_question_type(
            question_text, options_str, correct_answer
        )

        # 6. Создаем вопрос
        question = ZaekQuestion.objects.create(
            topic=topic,
            difficulty=difficulty,
            product=product,
            name=question_text,
            question_type=question_type,
            comment=row.get('Тема ответа', '')  # Сохраняем тему ответа как комментарий
        )

        # 7. Создаем ответы
        self._create_answers(question, question_type, options_str, correct_answer)

        return question

    def _determine_question_type(self, question_text, options_str, correct_answer):
        """Определение типа вопроса"""
        # Проверяем на соответствие
        if 'Соответствие' in question_text or 'Сопоставьте' in question_text:
            return 'match'

        # Если есть варианты ответов
        if options_str and options_str.strip():
            # Проверяем на множественный выбор
            correct_options = [opt.strip() for opt in correct_answer.split('|') if opt.strip()]
            if len(correct_options) > 1:
                return 'multiple'
            return 'single'

        # Иначе текстовый ответ
        return 'text'

    def _create_answers(self, question, question_type, options_str, correct_answer):
        """Создание ответов для вопроса"""
        options = [opt.strip() for opt in options_str.split('|') if opt.strip()] if options_str else []
        correct_options = [opt.strip() for opt in correct_answer.split('|') if opt.strip()] if correct_answer else []

        if question_type == 'text':
            # Текстовый ответ
            if correct_answer:
                ZaekAnswer.objects.create(
                    question=question,
                    text=correct_answer,
                    is_correct=True
                )
            else:
                ZaekAnswer.objects.create(
                    question=question,
                    text='',  # Пустой ответ для текстовых вопросов
                    is_correct=True
                )

        elif question_type == 'single':
            # Одиночный выбор
            if not options and correct_answer:
                options = [correct_answer]
                correct_options = [correct_answer]

            # Проверяем, что есть правильный ответ
            if not correct_options and options:
                correct_options = [options[0]]  # Берем первый вариант как правильный

            for option in options:
                is_correct = option in correct_options
                ZaekAnswer.objects.create(
                    question=question,
                    text=option,
                    is_correct=is_correct
                )

        elif question_type == 'multiple':
            # Множественный выбор
            if not options and correct_answer:
                # Если нет вариантов, но есть правильный ответ, разбиваем его на варианты
                options = correct_options

            for option in options:
                is_correct = option in correct_options
                ZaekAnswer.objects.create(
                    question=question,
                    text=option,
                    is_correct=is_correct
                )

        elif question_type == 'match':
            # Соответствие
            if not options and correct_answer:
                # Если нет вариантов, но есть правильный ответ
                options = correct_options

            # Для соответствия создаем пары: левая часть (неправильная) и правая (правильная)
            # или используем индексы для определения правильности
            for i, option in enumerate(options):
                # Для соответствия проверяем по индексу
                is_correct = False
                if i < len(correct_options):
                    # Проверяем, совпадает ли вариант с правильным ответом
                    if option == correct_options[i] or i % 2 == 0:
                        is_correct = True

                ZaekAnswer.objects.create(
                    question=question,
                    text=option,
                    is_correct=is_correct
                )

    def get_stats(self):
        """Получение статистики импорта"""
        return self.stats

    def get_summary(self):
        """Получение краткого отчета"""
        stats = self.stats
        summary = {
            'total': stats['total_rows'],
            'success': stats['success'],
            'errors': stats['errors'],
            'success_rate': '100%' if stats['total_rows'] == 0 else
                           f'{round((stats["success"] / stats["total_rows"]) * 100, 2)}%',
            'error_messages': stats['error_messages'][:5],  # Только первые 5 ошибок
            'has_more_errors': len(stats['error_messages']) > 5,
            'created_count': len(stats['created_questions'])
        }
        return summary