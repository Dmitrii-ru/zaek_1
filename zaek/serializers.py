from rest_framework import serializers
from .models import ZaekUser


class ZaekUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZaekUser
        fields = ['id_telegram', 'total_attempts', 'correct_attempts','name_telegram']


