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

    art  = models.CharField(
        verbose_name='Артикул',
        max_length=100,
        unique=True,
        blank=False,
        null=False,
        help_text='Уникальной артикул (макс. 100 символов)'
    )

    name = models.TextField(
        verbose_name='Название',
        unique=True,
        blank=False,
        null=False,
        help_text='Уникальное название'
    )
    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['name']

    def __str__(self):
        return f'{self.art} - {self.name}'

class ZaekQuestion(models.Model):
    topic = models.ForeignKey(
        ZaekTopic,
        verbose_name='Тема',
        on_delete=models.CASCADE,
        related_name='questions'
    )

    product = models.ForeignKey(
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
    created_at = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True
    )

    comment = models.TextField(
        verbose_name='Комментарий',
        blank=True,
        null=True,
        help_text='Комментарий'
    )

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['-created_at']
        unique_together = ['topic', 'name']  # Один вопрос в одной теме

    def __str__(self):
        return f'{self.topic.name}: {self.name[:50]}'



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
        help_text='Подробный текст ответа'
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

