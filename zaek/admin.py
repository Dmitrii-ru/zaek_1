

from django.contrib import admin
import nested_admin
from .models import ZaekTopic, ZaekProduct, ZaekQuestion, ZaekAnswer, TopicCategory, DifficultyLevel


class ZaekAnswerInline(nested_admin.NestedTabularInline):
    model = ZaekAnswer
    extra = 1
    fields = ['text', 'is_correct']
    verbose_name = "Ответ"
    verbose_name_plural = "Ответы"


class ZaekQuestionAdmin(nested_admin.NestedModelAdmin):
    list_display = ['name',  'product','difficulty']
    list_filter = ['product']
    search_fields = ['name']
    inlines = [ZaekAnswerInline]  # Вложенные ответы

    fieldsets = (
        (None, {
            'fields': ('name',  'product', 'comment')
        }),
    )


class ZaekQuestionInline(nested_admin.NestedTabularInline):
    model = ZaekQuestion
    extra = 1
    fields = ['name', 'topic', 'difficulty', 'image_url']
    inlines = [ZaekAnswerInline]
    verbose_name = "Вопрос"
    verbose_name_plural = "Вопросы"
    show_change_link = True


class ZaekProductAdmin(nested_admin.NestedModelAdmin):
    list_display = [ 'name']
    search_fields = ['name']
    inlines = [ZaekQuestionInline]  # Вложенные вопросы

    fieldsets = (
        (None, {
            'fields': ('category','name','image','image_url','comment')
        }),
    )


class ZaekTopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'comment']
    search_fields = ['name']



# Регистрация всех моделей
admin.site.register(ZaekTopic, ZaekTopicAdmin)
admin.site.register(ZaekProduct, ZaekProductAdmin)
admin.site.register(ZaekQuestion, ZaekQuestionAdmin)
admin.site.register(TopicCategory)
admin.site.register(DifficultyLevel)