import csv
import os
from io import TextIOWrapper
from django.db import transaction
from django.core.exceptions import ValidationError

# Импорт моделей
from zaek.models import (
    DifficultyLevel,
    TopicCategory,
    ZaekTopic,
    ZaekProduct,
    ZaekQuestion,
    ZaekAnswer
)


class CSVLoaderTEST:
    """Загрузка вопросов из CSV в базу данных"""

    # Разделитель колонок (в вашем CSV используется $)
    DELIMITER = '$'

    # Соответствие уровней сложности
    DIFFICULTY_MAPPING = {
        '1': 1,
        '2': 2,
        '3': 3,
        'легкий': 1,
        'средний': 2,
        'сложный': 3,
    }

    # Соответствие типов вопросов
    TYPE_MAPPING = {
        'выбор ответа': 'single',
        'множественный выбор': 'multiple',
        'текстовый ответ': 'text',
        'соответствие': 'match',
        'одиночный выбор': 'single',
    }

    def __init__(self, csv_file, user=None):
        self.csv_file = csv_file
        self.user = user
        self.stats = {
            'total_rows': 0,
            'success': 0,
            'errors': 0,
            'error_messages': [],
            'created_questions': 0,
            'created_answers': 0,
            'categories_created': 0,
            'products_created': 0,
            'topics_created': 0,
            'data': []
        }

        # Показываем информацию о файле
        if isinstance(csv_file, str):
            print(f'📖 Загрузка файла: {csv_file}')
            if os.path.exists(csv_file):
                print(f'✅ Файл найден. Размер: {os.path.getsize(csv_file)} байт')
            else:
                print(f'❌ Файл не найден')
                raise FileNotFoundError(f'Файл не найден: {csv_file}')

        self.read_csv()

    def _clean_value(self, value):
        """Очистка значения от лишних пробелов"""
        if value is None:
            return ''
        if isinstance(value, list):
            return '|'.join(str(v).strip() for v in value if v)
        if isinstance(value, (int, float)):
            return str(value)
        return str(value).strip()

    def _find_column(self, row, possible_names):
        """Найти значение колонки по возможным именам"""
        for name in possible_names:
            if name in row:
                value = row[name]
                cleaned = self._clean_value(value)
                if cleaned:
                    return cleaned
        return None

    def _get_or_create_category(self, name):
        """Получить или создать категорию"""
        if not name:
            return None

        name = self._clean_value(name)
        if not name:
            return None

        try:
            category, created = TopicCategory.objects.get_or_create(
                name=name
            )
            if created:
                self.stats['categories_created'] += 1
                print(f'  📁 Создана категория: {name}')
            return category
        except Exception as e:
            print(f'  ❌ Ошибка создания категории "{name}": {e}')
            return None

    def _get_or_create_difficulty(self, level_text):
        """Получить или создать уровень сложности"""
        if not level_text:
            level_text = '1'

        level_text = self._clean_value(level_text)
        if not level_text:
            level_text = '1'

        # Пробуем получить уровень из маппинга
        level_text_lower = level_text.lower()
        level = self.DIFFICULTY_MAPPING.get(level_text_lower)

        if level is None:
            try:
                level = int(level_text)
            except ValueError:
                print(f'  ⚠️ Неизвестный уровень сложности: {level_text}, используем 1')
                level = 1

        level = max(1, min(3, level))

        level_names = {
            1: 'Легкий',
            2: 'Средний',
            3: 'Сложный'
        }
        name = level_names.get(level, f'Уровень {level}')

        try:
            difficulty, created = DifficultyLevel.objects.get_or_create(
                level=level,
                defaults={'name': name}
            )
            if created:
                print(f'  📊 Создан уровень сложности: {name}')
            return difficulty
        except Exception as e:
            print(f'  ❌ Ошибка создания уровня сложности: {e}')
            return DifficultyLevel.objects.get_or_create(
                level=1,
                defaults={'name': 'Легкий'}
            )[0]

    def _get_or_create_product(self, category, product_name):
        """Получить или создать продукт"""
        if not category:
            return None

        product_name = self._clean_value(product_name)
        if not product_name:
            return None

        try:
            product, created = ZaekProduct.objects.get_or_create(
                name=product_name,
                category=category,

                defaults={

                    'comment': 'Создано из CSV'
                }
            )
            if created:
                self.stats['products_created'] += 1
                print(f'  📦 Создан продукт: {product_name}')
            return product
        except Exception as e:
            print(f'  ❌ Ошибка создания продукта: {e}')
            return None

    def _get_or_create_topic(self, name, comment=None):
        """Получить или создать тему"""
        if not name:
            return None

        name = self._clean_value(name)
        if not name:
            return None

        try:
            topic, created = ZaekTopic.objects.get_or_create(
                name=name,
                defaults={'comment': comment or ''}
            )
            if created:
                self.stats['topics_created'] += 1
                print(f'  📚 Создана тема: {name}')
            return topic
        except Exception as e:
            print(f'  ❌ Ошибка создания темы "{name}": {e}')
            return None

    # def _determine_type(self, answer_type, options, correct_answer):
    #     """Определить тип вопроса"""
    #     answer_type = self._clean_value(answer_type).lower()
    #
    #     # Проверяем по маппингу
    #     if answer_type in self.TYPE_MAPPING:
    #         return self.TYPE_MAPPING[answer_type]
    #
    #     # Проверяем по ключевым словам
    #     if 'множественный' in answer_type or 'несколько' in answer_type:
    #         return 'multiple'
    #     if 'текстовый' in answer_type:
    #         return 'text'
    #     if 'соответствие' in answer_type:
    #         return 'match'
    #
    #     # Автоматическое определение
    #     options_clean = self._clean_value(options)
    #     correct_clean = self._clean_value(correct_answer)
    #
    #     if options_clean and '|' in options_clean:
    #         if correct_clean and '|' in correct_clean:
    #             return 'multiple'
    #         return 'single'
    #     else:
    #         if not options_clean or options_clean == '-':
    #             return 'text'
    #         return 'single'
    #
    # def _parse_options(self, options_str):
    #     """Разобрать варианты ответов"""
    #     cleaned = self._clean_value(options_str)
    #     if not cleaned or cleaned == '-':
    #         return []
    #
    #     # Разделяем по |
    #     options = [opt.strip() for opt in cleaned.split('|') if opt.strip()]
    #     return options
    #
    # def _parse_correct_answers(self, correct_str):
    #     """Разобрать правильные ответы"""
    #     cleaned = self._clean_value(correct_str)
    #     if not cleaned:
    #         return []
    #
    #     answers = [ans.strip() for ans in cleaned.split('|') if ans.strip()]
    #     return answers

    def _get_or_create_question(self,
                                question_text,
                                product,
                                difficulty,
                                topic,
                                image_url,
                                question_type='single',
                                comment='Импорт из CSV'
                                ):
        """Получить или создать вопрос с обновлением атрибутов"""
        if not question_text:
            return None

        question_text = self._clean_value(question_text)
        if not question_text:
            return None

        # Формируем словарь для defaults
        defaults = {
            'difficulty': difficulty,
            'question_type': question_type,
            'topic': topic,
            'comment': comment
        }

        # Добавляем image_url только если он есть
        if image_url:
            defaults['image_url'] = image_url

        try:
            question, created = ZaekQuestion.objects.update_or_create(
                name=question_text,
                product=product,
                defaults=defaults
            )

            if created:
                self.stats['created_questions'] += 1
                print(f'  ✅ Создан вопрос: {question_text[:50]}...')
            else:
                print(f'  🔄 Обновлен вопрос: {question_text[:50]}...')

            return question

        except Exception as e:
            print(f'  ❌ Ошибка в _get_or_create_question: {e}')
            return None


    @transaction.atomic
    def _process_row(self, row, row_num):
        """Обработка строки CSV"""

        # Получаем данные из колонок (используем правильные названия из CSV)
        category_name = self._clean_value(row.get('Название категории', 'Базовая категория'))
        product_name = self._clean_value(row.get('Продукт', 'Базовый продукт'))
        difficulty_text = self._clean_value(row.get('Название уровня', 1))
        question_text = self._clean_value(row.get('Вопрос', ''))
        topic_type = self._clean_value(row.get('Тема ответа', ''))
        correct_answer = self._clean_value(row.get('Правильный ответ', ''))
        options = self._clean_value(row.get('Варианты ответов', ''))
        image_url=row.get("Ссылка на изображение",None)


        category = self._get_or_create_category(category_name)
        product = self._get_or_create_product(category,product_name)
        difficulty = self._get_or_create_difficulty(difficulty_text)




        if topic_type.lower() == 'выбор ответа':
            topic, created = ZaekTopic.objects.get_or_create(
                name="single",
            )

            question = self._get_or_create_question(
                question_text,
                product,
                difficulty,
                topic,
                image_url
            )

            # Создаем правильный ответ
            correct_ans, correct_updated = ZaekAnswer.objects.update_or_create(
                question=question,
                text=correct_answer,
                defaults={
                    'is_correct': True,
                }
            )

            list_id_opt = [correct_ans.pk]  # Сразу добавляем ID правильного ответа

            if options:
                # Разбиваем варианты ответов
                options_list = [opt.strip() for opt in options.split('|') if opt.strip()]

                for option in options_list:
                    # Пропускаем, если вариант совпадает с правильным ответом
                    if option == correct_answer:
                        print(f'  ⏭️ Пропускаем дубликат правильного ответа: {option}')
                        continue

                    false_ans, false_updated = ZaekAnswer.objects.update_or_create(
                        question=question,
                        text=option,
                        defaults={
                            'is_correct': False,
                        }
                    )
                    list_id_opt.append(false_ans.pk)

            # Удаляем все ответы, которых нет в списке
            deleted_count = ZaekAnswer.objects.filter(question=question).exclude(
                pk__in=list_id_opt
            ).delete()

            print(f'  🗑️ Удалено старых ответов: {deleted_count[0]}')
            print(f'  ✅ Правильный ответ: {correct_answer}')
            print(f'  📝 Варианты ответов: {options}')
            print(f'  📌 Вопрос: {question}')

    # question = self._get_or_create_question(
        #     question_text,
        #     product,
        #     difficulty,
        #     topic,
        # )

        # print(category,"category")
        # print(product,'product')
        # print(difficulty,'difficulty')
        # print(question,'question')



    def read_csv(self):
        """Чтение данных из CSV файла"""
        print('\n📖 Чтение CSV файла...213123123123')
        print('=' * 70)

        try:
            if isinstance(self.csv_file, str):
                file_obj = open(self.csv_file, 'r', encoding='utf-8-sig')
            else:
                file_obj = TextIOWrapper(self.csv_file.file, encoding='utf-8-sig')

            reader = csv.DictReader(file_obj, delimiter=self.DELIMITER)
            headers = reader.fieldnames

            print(f'📋 Заголовки: {headers}')
            print(f'📊 Количество колонок: {len(headers)}')
            print('=' * 70)

            for row_num, row in enumerate(reader, start=1):
                self.stats['total_rows'] += 1
                print(f'\n📌 Строка {row_num}/{row_num}')
                print(f'   Вопрос: {row.get("Вопрос", "")[:80]}...' if row.get("Вопрос") else '   Вопрос: (пусто)')
                print(f'   Категория: {row.get("Название категории", "")}')
                print(f'   Продукт: {row.get("Продукт", "")}')
                print(f'   Уровень: {row.get("Название уровня", "")}')
                print(f'   Тип: {row.get("Тема ответа", "")}')
                print('   ---')


                self._process_row(row, row_num)

            if isinstance(self.csv_file, str):
                file_obj.close()

            # Вывод статистики
            print('\n' + '=' * 70)
            print('📊 СТАТИСТИКА ЗАГРУЗКИ:')
            print(f'  📝 Всего строк: {self.stats["total_rows"]}')
            print(f'  ✅ Успешно: {self.stats["success"]}')
            print(f'  ❌ Ошибок: {self.stats["errors"]}')
            print(f'  📚 Создано вопросов: {self.stats["created_questions"]}')
            print(f'  💡 Создано ответов: {self.stats["created_answers"]}')
            print(f'  📁 Создано категорий: {self.stats["categories_created"]}')
            print(f'  📦 Создано продуктов: {self.stats["products_created"]}')
            print(f'  📚 Создано тем: {self.stats["topics_created"]}')
            print('=' * 70)

            if self.stats['error_messages']:
                print('\n⚠️ ОШИБКИ:')
                for error in self.stats['error_messages'][:10]:
                    print(f'  ❌ {error}')
                if len(self.stats['error_messages']) > 10:
                    print(f'  ... и еще {len(self.stats["error_messages"]) - 10} ошибок')

            return self.stats

        except Exception as e:
            print(f'\n❌ Ошибка: {str(e)}')
            import traceback
            traceback.print_exc()
            raise