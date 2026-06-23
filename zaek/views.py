from django.http import HttpResponse
from django.shortcuts import render

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# from .fanc import get_random_question_data
from .models import ZaekUser, ZaekQuestion, ZaekAnswer
from .serializers import ZaekUserSerializer
import random


class ZaekUserAPIView(APIView):
    def post(self, request):
        id_telegram = request.data.get('id_telegram')
        name_telegram = request.data.get('name_telegram')
        if not id_telegram:
            return Response({"error": "id_telegram is required"}, status=status.HTTP_400_BAD_REQUEST)

        user, created = ZaekUser.objects.get_or_create(
            id_telegram=id_telegram,
            defaults={
                'total_attempts': 0,
                'correct_attempts': 0,
                'show': True,
                'name_telegram' : name_telegram
            }
        )

        serializer = ZaekUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RandomQuestionAPIView(APIView):
    def get(self, request):
        questions = ZaekQuestion.objects.all()
        if not questions.exists():
            return Response({"error": "No questions available"}, status=404)

        random_question = random.choice(questions)
        answers = ZaekAnswer.objects.filter(question=random_question)

        question_data = {
            "product": random_question.product.name if random_question.product else None,
            "question": random_question.name,
            "comment": random_question.comment,
            "answers": [
                {
                    "text": answer.text,
                    "is_correct": answer.is_correct
                }
                for answer in answers
            ]
        }
        return Response(question_data)


class UpdateStatsView(APIView):
    def post(self, request):
        telegram_id = request.data.get('telegram_id')
        is_correct = request.data.get('is_correct')

        if not telegram_id:
            return Response(
                {"error": "telegram_id and is_correct are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = ZaekUser.objects.get(id_telegram=telegram_id)
            user.total_attempts += 1
            if is_correct:
                user.correct_attempts += 1
            user.save()
            print(user.correct_attempts,user.total_attempts)
            return Response({"status": "success"})
        except ZaekUser.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )


# async def test_func(request):
#     await get_random_question_data()
#     return HttpResponse("Hello, World!")
from django.shortcuts import render
from django.views import View
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.contrib import messages

from .forms import CSVUploadForm
from .utils.csv_loader import CSVLoader


@method_decorator(staff_member_required, name='dispatch')
class CSVUploadView(View):
    """View для загрузки CSV файла с вопросами"""

    def get(self, request):
        form = CSVUploadForm()
        return render(request, 'zaek_app/upload_csv.html', {'form': form})

    def post(self, request):
        form = CSVUploadForm(request.POST, request.FILES)

        if not form.is_valid():
            return render(request, 'zaek_app/upload_csv.html', {'form': form})

        csv_file = form.cleaned_data['csv_file']

        # Загружаем данные
        loader = CSVLoader(csv_file)
        result = loader.load()

        # Добавляем сообщение об успехе/ошибке
        if result['errors']:
            messages.error(request, f'Загрузка завершена с ошибками. Пропущено: {result["skipped"]}')
        else:
            messages.success(request,
                             f'Успешно загружено! Создано: {result["created"]}, Обновлено: {result["updated"]}')

        return render(request, 'zaek_app/upload_csv.html', {
            'form': form,
            'result': result,
        })
