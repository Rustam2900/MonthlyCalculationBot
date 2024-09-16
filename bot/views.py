from rest_framework.generics import RetrieveAPIView, ListCreateAPIView, ListAPIView
from bot.serializer import UserSerializer, MandatoryUserSerializer

from bot.models import User, MandatoryUser


class UserListCreateAPIView(ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserRetrieveAPIView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'pk'


class MandatoryUserListCreateView(ListCreateAPIView):
    queryset = MandatoryUser.objects.all()
    serializer_class = MandatoryUserSerializer
