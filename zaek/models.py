from django.db import models


class DifficultyLevel(models.Model):
    name = models.CharField(
        verbose_name='Уровень сложности',
        max_length=50,
        unique=True,
        blank=True,
        null=True,
    )

    level = models.PositiveIntegerField(
        verbose_name='Числовой уровень',
        unique=True,
        help_text='Число для сортировки (1-легкий, 2-средний, 3-сложный)'
    )

    class Meta:
        verbose_name = 'Уровень сложности'
        verbose_name_plural = 'Уровни сложности'
        ordering = ['level']

    def __str__(self):
        return f'{self.name} (уровень {self.level})'


class TopicCategory(models.Model):
    """Тематическая категория топиков"""
    name = models.CharField(
        verbose_name='Название категории',
        max_length=100,
        unique=True,
        help_text='Например: Программирование, Дизайн, Маркетинг'
    )

    class Meta:
        verbose_name = 'Категория темы'
        verbose_name_plural = 'Категории тем'
        ordering = ['name']

    def __str__(self):
        return self.name


class ZaekTopic(models.Model):
    name = models.CharField(
        verbose_name='Название темы',
        max_length=100,
        unique=True,
        blank=False,
        null=False,
        help_text='Уникальное название темы (макс. 100 символов)'
    )

    comment = models.TextField(
        verbose_name='Комментарий',
        blank=True,
        null=True,
        help_text='Дополнительный комментарий'
    )

    class Meta:
        verbose_name = 'Тема'
        verbose_name_plural = 'Темы'
        ordering = ['name']

    def __str__(self):
        return self.name


class ZaekProduct(models.Model):

    category = models.ForeignKey(
        TopicCategory,
        verbose_name='Категория',
        on_delete=models.CASCADE,
        related_name='products',  # ✅ Правильно: TopicCategory.products.all()
        help_text='Категория',
        blank=False,
        null=False,
    )

    name = models.TextField(
        verbose_name='Название',
        unique=True,
        blank=False,
        null=False,
        help_text='Уникальное название продукта'
    )

    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='products/',
        blank=True,
        null=True,
        help_text='Изображение продукта (необязательно)'
    )

    image_url = models.URLField(
        verbose_name='Ссылка на изображение',
        blank=True,
        null=True,
        help_text='Ссылка на изображение продукта (если нет загруженного файла)'
    )

    comment = models.TextField(
        verbose_name='Комментарий',
        blank=True,
        null=True,
        help_text='Дополнительный комментарий'
    )

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['name']

    def __str__(self):
        return f'{self.name}'  # ✅ Теперь поле art существует


class ZaekQuestion(models.Model):
    topic = models.ForeignKey(
        ZaekTopic,
        verbose_name='Тема',
        on_delete=models.CASCADE,
        related_name='questions',  #  ZaekTopic.questions.all()
        help_text='Тема вопроса',
        blank=False,
        null=False,
    )

    difficulty = models.ForeignKey(
        DifficultyLevel,
        verbose_name='Уровень сложности',
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        related_name='questions',
        help_text='Уровень сложности вопроса'
    )

    product = models.ForeignKey(
        ZaekProduct,
        verbose_name='Связанный продукт',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='questions',  # ZaekProduct.questions.all()
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

    def __str__(self):
        return f'{self.name[:50]}'  # ✅ Убрал лишний символ в начале


class ZaekAnswer(models.Model):
    question = models.ForeignKey(
        ZaekQuestion,
        verbose_name='Вопрос',
        on_delete=models.CASCADE,
        related_name='answers'  # ZaekQuestion.answers.all()
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
        verbose_name='Имя в Telegram',
        max_length=200,
        blank=False,
        null=False,
        help_text='Имя пользователя в Telegram'
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


class Reminder(models.Model):
    user = models.ForeignKey(
        ZaekUser,
        on_delete=models.CASCADE,
        related_name="reminders"  # ✅ Правильно: ZaekUser.reminders.all()
    )

    text = models.CharField(
        verbose_name="Текст",
        max_length=260
    )

    created_at = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Напоминание'
        verbose_name_plural = 'Напоминания'
        ordering = ['-created_at']

    def __str__(self):
        return f'Напоминание для {self.user.name_telegram}: {self.text[:30]}'

    def save(self, *args, **kwargs):
        """Переопределяем save для гарантии использования правильного времени"""
        from django.utils import timezone
        if not self.id:  # только при создании
            self.created_at = timezone.now()
        super().save(*args, **kwargs)