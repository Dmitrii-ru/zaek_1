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
    text = models.CharField(
        verbose_name='Ответ',
        max_length=255,
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



