# Generated by Django 5.0 on 2025-07-29 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zaek', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='zaekanswer',
            name='text',
            field=models.CharField(help_text='Подробный текст ответа', max_length=255, verbose_name='Ответ'),
        ),
        migrations.AlterField(
            model_name='zaekquestion',
            name='name',
            field=models.TextField(help_text='Текст вопроса (макс. 255 символов)', verbose_name='Вопрос'),
        ),
    ]
