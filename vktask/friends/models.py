from django.db.models import (
    Model,
    CharField,
    ForeignKey,
    TextChoices,
    DO_NOTHING,
)
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator


class UserModel(AbstractUser):
    username: CharField = CharField(max_length=15,
                                    unique=True,
                                    null=False,
                                    validators=[UnicodeUsernameValidator()],
                                    verbose_name="имя пользователя")
    friends: ForeignKey = ForeignKey("UserModel", on_delete=DO_NOTHING, verbose_name="друзья")


class FriendRequestModel(Model):
    class Status(TextChoices):
        ACCEPTED = "ac", "заявка принята"
        REJECTED = "rj", "заявка отказана"
        WAITING = "wt", "в ожидании"

    sender: ForeignKey = ForeignKey(UserModel,
                                    on_delete=DO_NOTHING,
                                    related_name="own_requests",
                                    verbose_name="отправитель заявки")
    receiver: ForeignKey = ForeignKey(UserModel,
                                      on_delete=DO_NOTHING,
                                      related_name="out_requests",
                                      verbose_name="получатель заявки")
    status: CharField = CharField(max_length=2,
                                  choices=Status.choices,
                                  default=Status.WAITING,
                                  verbose_name="статус заявки")
    content: CharField = CharField(max_length=50, blank=True, verbose_name="сопроводительный текст заявки")
