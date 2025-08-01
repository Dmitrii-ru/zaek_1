from django.contrib import admin
import nested_admin
from .models import ZaekTopic, ZaekProduct, ZaekQuestion, ZaekAnswer

class ZaekAnswerInline(nested_admin.NestedTabularInline):
    model = ZaekAnswer
    extra = 1
    fields = ['text', 'is_correct']
    verbose_name = "Ответ"
    verbose_name_plural = "Ответы"

class ZaekQuestionInline(nested_admin.NestedTabularInline):
    model = ZaekQuestion
    extra = 1
    fields = ['name', 'topic', 'comment']
    inlines = [ZaekAnswerInline]  # Вложенные инлайны для ответов
    verbose_name = "Вопрос"
    verbose_name_plural = "Вопросы"

class ZaekProductAdmin(nested_admin.NestedModelAdmin):
    list_display = ['art', 'name']
    search_fields = ['art', 'name']
    inlines = [ZaekQuestionInline]  # Основные инлайны для вопросов

class ZaekTopicAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

admin.site.register(ZaekTopic, ZaekTopicAdmin)
admin.site.register(ZaekProduct, ZaekProductAdmin)