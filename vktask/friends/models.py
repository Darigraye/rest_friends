from django.db.models import (
    Model,
    CharField,
    ForeignKey,
    ManyToManyField,
    TextChoices,
    DO_NOTHING,
    CheckConstraint,
    Q,
    F,
)
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator


class UserModel(AbstractUser):
    username: CharField = CharField(max_length=15,
                                    unique=True,
                                    null=False,
                                    validators=[UnicodeUsernameValidator()],
                                    verbose_name="имя пользователя")
    friends: ManyToManyField = ManyToManyField("UserModel", blank=True, symmetrical=True, verbose_name="друзья")

    def __str__(self):
        return self.username

    class Meta:
        db_table = "User"
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"


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

    def __str__(self):
        return f"{self.pk}.от {self.sender} к {self.receiver}"

    class Meta:
        db_table = "FriendRequest"
        verbose_name = "запрос в друзья"
        verbose_name_plural = "запросы в друзья"
        constraints = [
            CheckConstraint(
                check=~Q(receiver_id=F("sender_id")),
                name="check_the_same_user"
            ),
        ]
