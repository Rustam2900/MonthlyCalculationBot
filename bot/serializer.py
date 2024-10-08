from rest_framework import serializers
from bot.models import User, MandatoryUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'telegram_id',
            'name',
            'username',
        ]


class MandatoryUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MandatoryUser
        fields = ['id', 'chat_id', 'name', 'url', 'channel_id']
