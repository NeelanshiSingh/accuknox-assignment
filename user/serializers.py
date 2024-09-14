from rest_framework import serializers
from user.models import User, FriendRequest


class GetUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password',]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'password',]
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True},
        }


class FriendRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = FriendRequest
        fields = [
            'id', 
            'requester', 
            'recipient', 
            'request_status', 
            'created_at'
        ]
        extra_kwargs = {
            'id': {'read_only': True},
            'requester': {'read_only': True},
            'request_status': {'read_only': True},
            'created_at': {'read_only': True}
        }


class SentFriendRequestSerializer(FriendRequestSerializer):
    recipient = UserSerializer(many=False)


class ReceivedFriendRequestSerializer(FriendRequestSerializer):
    requester = UserSerializer(many=False)


class FriendRequestHandleSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    action = serializers.ChoiceField(
        choices=['accepted', 'rejected'], 
        required=True
    )