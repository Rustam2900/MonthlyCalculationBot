from django.urls import path
from bot.views import (UserRetrieveAPIView, UserListCreateAPIView, MandatoryUserListCreateView, )

urlpatterns = [
    path('user-create/', UserListCreateAPIView.as_view(), name='user-create'),
    path('user/<int:pk>', UserRetrieveAPIView.as_view()),
    path('mandatory-users/', MandatoryUserListCreateView.as_view(), name='mandatory-user-list-create'),

]
