from django.urls import path
from bot.views import (UserRetrieveAPIView, UserListCreateAPIView, MandatoryUserListCreateView, UserListUpdateAPIView, )

urlpatterns = [
    path('user-create/', UserListCreateAPIView.as_view(), name='user-create'),
    path('user-update/<int:telegram_id>/', UserListUpdateAPIView.as_view(), name='user-create'),
    path('user/<int:telegram_id>', UserRetrieveAPIView.as_view()),
    path('mandatory-users/', MandatoryUserListCreateView.as_view(), name='mandatory-user-list-create'),

]
