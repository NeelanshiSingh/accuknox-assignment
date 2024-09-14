from django.urls import path
from user.views import GetUserAPIView, RegisterUserAPIView, \
    FetchAllUserAPIView, SendFriendRequestView,\
    HandleFriendRequestView, ListSentRequestsView, \
    ListReceivedRequestsView, ListFriendsView


urlpatterns = [
    path('user/', GetUserAPIView.as_view()),
    path('user/create/', RegisterUserAPIView.as_view()),
    path('user/all/', FetchAllUserAPIView.as_view()),
    path('send-friend-request/', SendFriendRequestView.as_view(), name='send_friend_request'),
    path('all-friends/', ListFriendsView.as_view(), name='list_friends'),
    path('all-sent/', ListSentRequestsView.as_view(), name='list_sent'),
    path('all-received/', ListReceivedRequestsView.as_view(), name='list_received'),
    path('handle-friend-requests/', HandleFriendRequestView.as_view(), name='handle_friend_request'),
]
