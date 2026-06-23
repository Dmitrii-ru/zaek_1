import csv
import io
from django.db import transaction
from django.core.exceptions import ValidationError
from ..models import (
    TopicCategory,
    ZaekProduct,
    ZaekTopic,
    DifficultyLevel,
    ZaekQuestion,
    ZaekAnswer
)


class CSVLoader:
    """Класс для загрузки данных из CSV в базу данных"""

    # Маппинг колонок из CSV на поля моделей
    COLUMN_MAPPING = {
        'Название категории': 'category_name',
        'Продукт': 'product_name',
        'Вопрос': 'question_text',
        'Ответ': 'answer_text',
        'Тема вопроса': 'topic_name',
        'Уровень сложности': 'difficulty_level',
        'Ссылка на изображение': 'image_url',  # НОВАЯ КОЛОНКА
        'Image URL': 'image_url',  # Альтернативное название
        'image_url': 'image_url',  # Альтернативное название
    }

    # Разделитель колонок
    DELIMITER = '$'

    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.errors = []
        self.created_count = 0
        self.updated_count = 0
        self.skipped_count = 0

    def _parse_csv(self):
        """Парсит CSV файл и возвращает список словарей"""
        try:
            # Пробуем разные кодировки
            for encoding in ['utf-8-sig', 'utf-8', 'cp1251']:
                try:
                    self.csv_file.seek(0)
                    content = self.csv_file.read().decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ValidationError('Не удалось определить кодировку файла. Используйте UTF-8 или Windows-1251.')

            # Парсим CSV с разделителем $
            reader = csv.DictReader(
                io.StringIO(content),
                delimiter=self.DELIMITER,
                quotechar='"',
                quoting=csv.QUOTE_MINIMAL
            )

            # Проверяем наличие необходимых колонок
            required_columns = ['Название категории', 'Продукт', 'Вопрос', 'Ответ']
            actual_columns = reader.fieldnames or []

            missing_columns = [col for col in required_columns if col not in actual_columns]
            if missing_columns:
                raise ValidationError(
                    f'В файле отсутствуют обязательные колонки: {", ".join(missing_columns)}. '
                    f'Доступны: {", ".join(actual_columns)}'
                )

            return list(reader)

        except Exception as e:
            raise ValidationError(f'Ошибка при парсинге CSV: {str(e)}')

    def _get_or_create_category(self, name):
        """Получает или создает категорию"""
        if not name or not name.strip():
            return None

        name = name.strip()
        category, created = TopicCategory.objects.get_or_create(
            name=name,
            defaults={'name': name}
        )
        if created:
            self.created_count += 1
        return category

    def _get_or_create_product(self, category, name):
        """Получает или создает продукт"""
        if not name or not name.strip():
            return None

        name = name.strip()
        product, created = ZaekProduct.objects.get_or_create(
            name=name,
            defaults={
                'category': category,
                'name': name,
            }
        )
        if created:
            self.created_count += 1
        elif category and product.category != category:
            # Обновляем категорию у существующего продукта
            product.category = category
            product.save()
            self.updated_count += 1
        return product

    def _get_or_create_topic(self, name):
        """Получает или создает тему вопроса"""
        if not name or not name.strip():
            return None

        name = name.strip()
        topic, created = ZaekTopic.objects.get_or_create(
            name=name,
            defaults={'name': name}
        )
        if created:
            self.created_count += 1
        return topic

    def _get_or_create_difficulty(self, level_value):
        """Получает или создает уровень сложности"""
        try:
            level = int(level_value)
        except (ValueError, TypeError):
            # Если не число, пробуем найти по имени
            if level_value and str(level_value).strip():
                name = str(level_value).strip()
                difficulty, created = DifficultyLevel.objects.get_or_create(
                    name=name,
                    defaults={'level': 1, 'name': name}
                )
                if created:
                    self.created_count += 1
                return difficulty
            return None

        # Ищем по уровню
        try:
            difficulty = DifficultyLevel.objects.get(level=level)
            return difficulty
        except DifficultyLevel.DoesNotExist:
            # Создаем новый уровень
            name = f'Уровень {level}'
            difficulty = DifficultyLevel.objects.create(
                name=name,
                level=level
            )
            self.created_count += 1
            return difficulty

    def _get_image_url(self, row):
        """
        Извлекает URL изображения из строки CSV.
        Проверяет несколько возможных названий колонок.
        """
        # Возможные названия колонок для изображения
        possible_columns = ['Ссылка на изображение', 'Image URL', 'image_url', 'Картинка', 'Изображение']

        for col in possible_columns:
            if col in row and row[col] and row[col].strip():
                url = row[col].strip()
                # Простая валидация URL
                if url.startswith(('http://', 'https://', '/')):
                    return url
                else:
                    self.errors.append(f'Неверный формат URL: "{url}"')
                    return None

        return None

    def _process_row(self, row):
        """Обрабатывает одну строку CSV"""
        # Извлекаем данные из строки
        category_name = row.get('Название категории', '').strip()
        product_name = row.get('Продукт', '').strip()
        question_text = row.get('Вопрос', '').strip()
        answer_text = row.get('Ответ', '').strip()
        topic_name = row.get('Тема вопроса', '').strip()
        difficulty_level = row.get('Уровень сложности', '').strip()
        image_url = self._get_image_url(row)  # НОВОЕ: извлекаем URL изображения

        # Проверяем обязательные поля
        if not question_text:
            self.errors.append(f'Пропущен вопрос в строке: {row}')
            self.skipped_count += 1
            return

        if not answer_text:
            self.errors.append(f'Пропущен ответ для вопроса: "{question_text[:50]}..."')
            self.skipped_count += 1
            return

        try:
            with transaction.atomic():
                # Получаем или создаем связанные объекты
                category = self._get_or_create_category(category_name) if category_name else None
                product = self._get_or_create_product(category, product_name) if product_name else None
                topic = self._get_or_create_topic(topic_name) if topic_name else None
                difficulty = self._get_or_create_difficulty(difficulty_level) if difficulty_level else None

                # Если нет уровня сложности, используем уровень 1
                if not difficulty:
                    difficulty, _ = DifficultyLevel.objects.get_or_create(
                        level=1,
                        defaults={'name': 'Базовый', 'level': 1}
                    )
                    if _:
                        self.created_count += 1

                # Ищем существующий вопрос по тексту
                question, created = ZaekQuestion.objects.get_or_create(
                    name=question_text,
                    defaults={
                        'topic': topic,
                        'difficulty': difficulty,
                        'product': product,
                        'image_url': image_url,  # НОВОЕ: добавляем при создании
                        'comment': f'Загружен из CSV. Категория: {category_name}',
                    }
                )

                if created:
                    self.created_count += 1
                else:
                    # Обновляем существующий вопрос
                    self.updated_count += 1
                    if topic:
                        question.topic = topic
                    if difficulty:
                        question.difficulty = difficulty
                    if product:
                        question.product = product
                    # НОВОЕ: обновляем image_url, если он передан и не пустой
                    if image_url:
                        question.image_url = image_url
                    question.save()

                # Обновляем ответы: удаляем старые правильные ответы и создаем новый
                # (поскольку по условию только один правильный ответ)
                ZaekAnswer.objects.filter(
                    question=question,
                    is_correct=True
                ).delete()

                # Создаем новый правильный ответ
                ZaekAnswer.objects.create(
                    question=question,
                    text=answer_text,
                    is_correct=True
                )

        except Exception as e:
            self.errors.append(f'Ошибка при обработке вопроса "{question_text[:50]}...": {str(e)}')
            self.skipped_count += 1

    def load(self):
        """Основной метод загрузки данных"""
        rows = self._parse_csv()

        total = len(rows)
        for i, row in enumerate(rows, 1):
            self._process_row(row)

        return {
            'total': total,
            'created': self.created_count,
            'updated': self.updated_count,
            'skipped': self.skipped_count,
            'errors': self.errors,
        }