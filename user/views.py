from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Q, Case, When, Value, IntegerField
from user.serializers import GetUserSerializer, UserSerializer, \
    FriendRequestSerializer, FriendRequestHandleSerializer, \
    SentFriendRequestSerializer, ReceivedFriendRequestSerializer
from user.models import User, FriendRequest
from datetime import timedelta
from django.utils import timezone
from rest_framework.generics import GenericAPIView


class GetMixin:
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class GetUserAPIView(GenericAPIView):
    serializer_class = GetUserSerializer
    permission_classes = [permissions.IsAuthenticated,]

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class RegisterUserAPIView(GenericAPIView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FetchAllUserAPIView(GenericAPIView, GetMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated,]

    def get_queryset(self):
        queryset = super().get_queryset()
        search_keyword = self.request.query_params.get('search', '')
        if not search_keyword:
            return queryset

        if '@' in search_keyword:
            return queryset.filter(email__iexact=search_keyword)
        return queryset.filter(
            Q(first_name__icontains=search_keyword) | Q(last_name__icontains=search_keyword)
        )


class SendFriendRequestView(GenericAPIView):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated,]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            recipient = serializer.validated_data.get('recipient')
            if recipient == request.user:
                return Response({
                    "error": "Cannot send request to yourself"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            one_minute_ago = timezone.now() - timedelta(minutes=1)
            recent_requests = FriendRequest.objects.filter(
                requester=request.user, created_at__gte=one_minute_ago
            ).count()

            if recent_requests >= 3:
                return Response({
                    "error": "You can't send more than 3 friend requests per minute."
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)

            friend_request, created = FriendRequest.objects.get_or_create(
                requester=request.user, recipient=recipient, request_status='pending'
            )

            if not created:
                return Response({
                    "error": "Friend request already sent."
                }, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Friend request sent."}, status=status.HTTP_201_CREATED)


class HandleFriendRequestView(GenericAPIView):
    serializer_class = FriendRequestHandleSerializer
    permission_classes = [permissions.IsAuthenticated,]

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                id = serializer.validated_data.get('id')
                action = serializer.validated_data.get('action')
                frnd_rqst = FriendRequest.objects.get(
                    id=id, 
                    request_status='pending', 
                    recipient=request.user
                )
                if action == 'accepted':
                    frnd_rqst.request_status = 'accepted'
                    frnd_rqst.save()
                    return Response({
                        "message": "Friend request accepted."
                    }, status=status.HTTP_200_OK)

                frnd_rqst.request_status = 'rejected'
                frnd_rqst.save()
                return Response({
                    "message": "Friend request rejected."
                }, status=status.HTTP_200_OK)
                
        except:
            return Response({
                "message": "No pending friend request found with id"
            }, status=status.HTTP_400_BAD_REQUEST)


class ListFriendRequestsView(GenericAPIView, GetMixin):
    queryset = FriendRequest.objects.all()
    permission_classes = [permissions.IsAuthenticated,]


class ListSentRequestsView(ListFriendRequestsView):
    serializer_class = SentFriendRequestSerializer
    def get_queryset(self):
        return self.queryset.filter(requester=self.request.user, request_status='pending')


class ListReceivedRequestsView(ListFriendRequestsView):
    serializer_class = ReceivedFriendRequestSerializer
    def get_queryset(self):
        return self.queryset.filter(recipient=self.request.user, request_status='pending')


class ListFriendsView(GenericAPIView, GetMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated,]

    def get_queryset(self):
        friend_ids = FriendRequest.objects.filter(
            recipient=self.request.user, 
            request_status='accepted'
        ).annotate(
            relevant_id=Case(
                When(requester=self.request.user, then='recipient__id'),
                When(recipient=self.request.user, then='requester__id'),
                output_field=IntegerField()
            )
        ).values_list(
            'relevant_id',
            flat=True
        )
        return self.queryset.filter(id__in=friend_ids)



