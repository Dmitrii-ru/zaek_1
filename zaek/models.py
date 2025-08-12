from django.db import models

class ZaekTopic(models.Model):
    name = models.CharField(
        verbose_name='Название темы',
        max_length=100,
        unique=True,
        blank=False,
        null=False,
        help_text='Уникальное название темы (макс. 100 символов)'
    )

    class Meta:
        verbose_name = 'Тема'
        verbose_name_plural = 'Темы'
        ordering = ['name']

    def __str__(self):
        return self.name

class ZaekProduct(models.Model):
    art = models.CharField(
        verbose_name='Артикул',
        max_length=100,
        unique=True,
        blank=False,
        null=False,
        help_text='Уникальный артикул (макс. 100 символов)'
    )

    name = models.TextField(
        verbose_name='Название',
        unique=True,
        blank=False,
        null=False,
        help_text='Уникальное название продукта'
    )

    topic = models.ForeignKey(  # Изменено на ForeignKey (один продукт - одна тема)
        ZaekTopic,
        verbose_name='Тема',
        related_name='products',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='Тема, к которой относится продукт'
    )

    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='products/',
        blank=True,
        null=True,
        help_text='Изображение продукта (необязательно)'
    )

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['name']

    def __str__(self):
        return f'{self.art} - {self.name}'

class ZaekQuestion(models.Model):
    topic = models.ForeignKey(  # Восстановлена связь с темой
        ZaekTopic,
        verbose_name='Тема',
        on_delete=models.CASCADE,
        related_name='questions',
        help_text='Тема вопроса',
        null=True
    )

    product = models.ForeignKey(  # Оставлена связь с продуктом (если нужна)
        ZaekProduct,
        verbose_name='Связанный продукт',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='questions',
        help_text='Необязательная привязка к продукту'
    )

    name = models.TextField(
        verbose_name='Вопрос',
        blank=False,
        null=False,
        help_text='Текст вопроса'
    )

    comment = models.TextField(
        verbose_name='Комментарий',
        blank=True,
        null=True,
        help_text='Дополнительный комментарий'
    )

    created_at = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['-created_at']
        unique_together = ['topic', 'name']

    def __str__(self):
        return f': {self.name[:50]}'

# Остальные модели (ZaekAnswer, ZaekUser) остаются без изменений

class ZaekAnswer(models.Model):
    question = models.ForeignKey(
        ZaekQuestion,
        verbose_name='Вопрос',
        on_delete=models.CASCADE,
        related_name='answers'
    )

    text = models.TextField(
        verbose_name='Ответ',
        blank=False,
        null=False,
        max_length=500,
        help_text='Текст ответа'
    )

    is_correct = models.BooleanField(
        verbose_name='Правильный ответ',
        default=False
    )

    created_at = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'
        ordering = ['-is_correct', 'created_at']

    def __str__(self):
        return f'Ответ на "{self.question.name[:30]}..."'

# Модель ZaekUser остаётся без изменений


class ZaekUser(models.Model):
    id_telegram = models.CharField(
        verbose_name='ID в Telegram',
        max_length=30,
        blank=False,
        null=False,
        unique=True,
        help_text='Уникальный идентификатор пользователя в Telegram'
    )

    name_telegram = models.CharField(
        verbose_name='Имя в телегам в Telegram',
        max_length=200,
        blank=False,
        null=False,
        unique=True,
        help_text='Уникальный идентификатор пользователя в Telegram'
    )

    total_attempts = models.PositiveIntegerField(
        verbose_name='Всего попыток',
        default=0,
        help_text='Общее количество данных пользователем ответов'
    )

    correct_attempts = models.PositiveIntegerField(
        verbose_name='Правильные ответы',
        default=0,
        help_text='Количество верных ответов пользователя'
    )

    created_at = models.DateTimeField(
        verbose_name='Дата регистрации',
        auto_now_add=True
    )

    last_activity = models.DateTimeField(
        verbose_name='Последняя активность',
        auto_now=True,
        help_text='Время последнего взаимодействия с ботом'
    )

    show = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['id_telegram']),
        ]

    def __str__(self):
        return f'Пользователь Telegram (ID: {self.id_telegram} - {self.name_telegram})'

    def increment_attempts(self, is_correct: bool):
        self.total_attempts += 1
        if is_correct:
            self.correct_attempts += 1
        self.save()

    @property
    def success_rate(self) -> float:
        if self.total_attempts == 0:
            return 0.0
        return round((self.correct_attempts / self.total_attempts) * 100, 2)

