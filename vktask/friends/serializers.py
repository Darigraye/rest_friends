from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import(
    ModelSerializer,
    HiddenField,
    CurrentUserDefault,
    ValidationError,
    CharField
)
from .models import UserModel, FriendRequestModel


class UserSerializer(ModelSerializer):
    def create(self, validated_data):
        return UserModel.objects.create_user(
            **validated_data
        )

    class Meta:
        model = UserModel
        fields = ("id", "username", "email", "first_name", "last_name", "last_login", "password")
        extra_kwargs = {"password": {"write_only": True}}


class FriendRequestSerializer(ModelSerializer):
    receiver: SlugRelatedField = SlugRelatedField(slug_field="username", queryset=UserModel.objects.all())
    sender: HiddenField = HiddenField(default=CurrentUserDefault())
    status: HiddenField = HiddenField(default=FriendRequestModel.Status.WAITING)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["sender"] = instance.sender.username
        rep["receiver"] = instance.receiver.username
        return rep

    def validate(self, data):
        if data["sender"] == data["receiver"]:
            raise ValidationError("вы не можете отправлять запросы в друзья самому себе")

        if UserModel.objects.filter(username=data["sender"], friends__username=data["receiver"]).exists():
            raise ValidationError("этот человек уже есть у вас в друзьях")

        if FriendRequestModel.objects.filter(receiver=data["receiver"],
                                             sender=data["sender"],
                                             status=FriendRequestModel.Status.WAITING).exists():
            raise ValidationError("вы уже отправили заявку пользователю")

        return data

    class Meta:
        model = FriendRequestModel
        fields = "__all__"


class IncomingFriendRequestSerializer(ModelSerializer):
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["sender"] = instance.sender.username
        return rep

    class Meta:
        model = FriendRequestModel
        fields = ("id", "sender", "content")


class OutgoingFriendRequestSerializer(ModelSerializer):
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["receiver"] = instance.receiver.username
        return rep

    class Meta:
        model = FriendRequestModel
        fields = ("id", "receiver", "content")
