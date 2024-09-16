from rest_framework.generics import RetrieveAPIView, ListCreateAPIView, ListAPIView, UpdateAPIView
from bot.serializer import UserSerializer, MandatoryUserSerializer

from bot.models import User, MandatoryUser


class UserListCreateAPIView(ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserListUpdateAPIView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'telegram_id'


class UserRetrieveAPIView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'telegram_id'


class MandatoryUserListCreateView(ListCreateAPIView):
    queryset = MandatoryUser.objects.all()
    serializer_class = MandatoryUserSerializer
