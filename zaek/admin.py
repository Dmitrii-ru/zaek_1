# from django.contrib import admin
# import nested_admin
# from .models import ZaekTopic, ZaekProduct, ZaekQuestion, ZaekAnswer
#
# class ZaekAnswerInline(nested_admin.NestedTabularInline):
#     model = ZaekAnswer
#     extra = 1
#     fields = ['text', 'is_correct']
#     verbose_name = "Ответ"
#     verbose_name_plural = "Ответы"
#
# class ZaekQuestionInline(nested_admin.NestedTabularInline):
#     model = ZaekQuestion
#     extra = 1
#     fields = ['name', 'topic', 'comment']
#     inlines = [ZaekAnswerInline]  # Вложенные инлайны для ответов
#     verbose_name = "Вопрос"
#     verbose_name_plural = "Вопросы"
#
# class ZaekProductAdmin(nested_admin.NestedModelAdmin):
#     list_display = ['art', 'name']
#     search_fields = ['art', 'name']
#     inlines = [ZaekQuestionInline]  # Основные инлайны для вопросов
#
# class ZaekTopicAdmin(admin.ModelAdmin):
#     list_display = ['name']
#     search_fields = ['name']
#
# admin.site.register(ZaekTopic, ZaekTopicAdmin)
# admin.site.register(ZaekProduct, ZaekProductAdmin)


from django.contrib import admin
import nested_admin
from .models import ZaekTopic, ZaekProduct, ZaekQuestion, ZaekAnswer


class ZaekAnswerInline(nested_admin.NestedTabularInline):
    model = ZaekAnswer
    extra = 1
    fields = ['text', 'is_correct']
    verbose_name = "Ответ"
    verbose_name_plural = "Ответы"


class ZaekQuestionAdmin(nested_admin.NestedModelAdmin):
    list_display = ['name',  'product']
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
    fields = ['name', 'comment']
    inlines = [ZaekAnswerInline]  # Вложенные ответы
    verbose_name = "Вопрос"
    verbose_name_plural = "Вопросы"
    show_change_link = True  # Добавляет ссылку на отдельное редактирование


class ZaekProductAdmin(nested_admin.NestedModelAdmin):
    list_display = ['art', 'name']
    search_fields = ['art', 'name']
    inlines = [ZaekQuestionInline]  # Вложенные вопросы

    fieldsets = (
        (None, {
            'fields': ('art', 'name', 'image','topic')
        }),
    )


class ZaekTopicAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


# Регистрация всех моделей
admin.site.register(ZaekTopic, ZaekTopicAdmin)
admin.site.register(ZaekProduct, ZaekProductAdmin)
admin.site.register(ZaekQuestion, ZaekQuestionAdmin)