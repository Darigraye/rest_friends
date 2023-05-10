from django.core.exceptions import ObjectDoesNotExist

from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status

from .models import UserModel, FriendRequestModel
from .serializers import (UserSerializer,
                          FriendRequestSerializer,
                          IncomingFriendRequestSerializer,
                          OutgoingFriendRequestSerializer
                          )


class UserViewSet(viewsets.ModelViewSet):
    """
    Viewset which provides interaction with UserModel
    (auth., registration, deleting user etc.) by methods
     GET, POST, PUT, PATCH, DELETE
    """
    serializer_class = UserSerializer
    queryset = UserModel.objects.all()


class MakeFriendRequest(CreateAPIView):
    """
    Provides interface for sending friend request
    """
    serializer_class = FriendRequestSerializer
    queryset = FriendRequestModel.objects.all()
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        res = super().post(request, *args, **kwargs)

        try:
            request_from_one_to_another: FriendRequestModel = FriendRequestModel.objects.get(
                receiver=request.user.pk,
                sender__username=request.data.get("receiver"),
                status=FriendRequestModel.Status.WAITING
            )
        except ObjectDoesNotExist:
            pass
        else:
            request_from_another: FriendRequestModel = FriendRequestModel.objects.get(
                receiver__username=request.data.get("receiver"),
                sender=request.user.pk,
                status=FriendRequestModel.Status.WAITING
            )

            request_from_another.status = FriendRequestModel.Status.ACCEPTED
            request_from_one_to_another.status = FriendRequestModel.Status.ACCEPTED
            request_from_another.receiver.friends.add(request_from_another.sender)

            request_from_one_to_another.save()
            request_from_another.save()

        return res


class ListIncomingRequests(ListAPIView):
    """
    Represents incoming friend requests for current user
    """
    serializer_class = IncomingFriendRequestSerializer
    queryset = FriendRequestModel.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return FriendRequestModel.objects.filter(receiver=self.request.user.pk,
                                                 status=FriendRequestModel.Status.WAITING)


class ListOutgoingRequests(ListIncomingRequests):
    """
    Represents outgoing friend requests for current user
    """
    serializer_class = OutgoingFriendRequestSerializer

    def get_queryset(self):
        return FriendRequestModel.objects.filter(sender=self.request.user.pk,
                                                 status=FriendRequestModel.Status.WAITING)


class ListFriends(ListAPIView):
    """
    Represents every user who is friend of current user
    """
    queryset = FriendRequestModel.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return UserModel.objects.filter(friends__username=self.request.user.username)


class UserFriendStatus(APIView):
    """
    Responses status of adressed user:
    friend, incoming req., outgoing req. nothing
    """
    permission_classes = (IsAuthenticated, )
    def get(self, request, *args, **kwargs):
        friend_name = kwargs.get("username", None)

        if friend_name == request.user.username:
            return Response({"status": "это вы"})

        response_dict = {"user": friend_name}

        if not UserModel.objects.filter(username=friend_name).exists():
            return Response({"status": "ошибка, пользователя с указанными юзернеймом не существует"})
        elif UserModel.objects.filter(username=friend_name, friends__username=request.user.username).exists():
            response_dict.update({"status": "ваш друг"})
            return Response(response_dict)
        elif FriendRequestModel.objects.filter(sender__username=request.user.username,
                                               receiver__username=friend_name,
                                               status=FriendRequestModel.Status.WAITING).exists():
            response_dict.update({"status": "вами была отправлена заявка в друзья"})
            return Response(response_dict)
        elif FriendRequestModel.objects.filter(sender__username=friend_name,
                                               receiver__username=request.user.username,
                                               status=FriendRequestModel.Status.WAITING).exists():
            response_dict.update({"status": "вам была отправлена завка в друзья от этого "
                                            "пользователя"})
            return Response(response_dict)

        response_dict.update({"status": "нет в ваших друзьях, заявок нет"})
        return Response(response_dict)


class ResponseToFriendRequest(APIView):
    """
    Provides interface for response on friend request
    from certain user
    """
    queryset = FriendRequestModel.objects.all()
    permission_classes = (IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        sender = request.data.get("username")
        confrim = request.data.get("confrim")

        if sender is None:
            return Response({"sender": "поле обязательно для заполнения"})
        if confrim is None:
            return Response({"confrim": "поле обязательно для заполнения"})

        try:
            friend_request = FriendRequestModel.objects.get(
                                           sender__username=sender,
                                           receiver__username=request.user.username,
                                           status=FriendRequestModel.Status.WAITING
                                           )
        except:
            return Response({
                             "status": "не было найдено запросов на дружбу от указанного пользователя",
                             "sender": sender
            })
        else:
            if confrim:
                friend_request.status = FriendRequestModel.Status.ACCEPTED
                friend_request.receiver.friends.add(friend_request.sender)
                friend_request.save()
                status = "Пользователь успешно добавлен в друзья"
            else:
                friend_request.status = FriendRequestModel.Status.REJECTED
                status = "Заявка в друзья отклонена"

            return Response({
                "status": status,
                "sender": sender,
            })


class DeleteFromFriends(DestroyAPIView):
    """
    Provide interface for delete user from
    friends
    """
    permission_classes = (IsAuthenticated, )
    serializer_class = UserSerializer

    def destroy(self, request, *args, **kwargs):
        friends_username = request.data.get("username")
        if friends_username is None:
            return Response({"username": "поле обязательно для ввода"})

        if friends_username == request.user.username:
            return Response({"status": "это вы"})

        try:
            friend = UserModel.objects.get(username=friends_username, friends__username=request.user.username)
        except:
            return Response({"status": "такого пользователя у вас нет в друзьях", "username": friends_username})
        else:
            friend.friends.remove(request.user)
            return Response({"status": "пользователь успешно удалён из друзей", "ex-friend": friends_username})
