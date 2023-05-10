from django.urls import path, include
from rest_framework.authtoken import views
from rest_framework import routers

from .views import (
    UserViewSet,
    MakeFriendRequest,
    ListIncomingRequests,
    ListOutgoingRequests,
    ListFriends,
    UserFriendStatus,
    ResponseToFriendRequest,
    DeleteFromFriends,
)

router = routers.SimpleRouter()
router.register(r"users", UserViewSet, basename="users")

urlpatterns = [
    path("", include(router.urls)),
    path("login/", views.obtain_auth_token),
    path("send_friend_request/", MakeFriendRequest.as_view()),
    path("incoming_requests/", ListIncomingRequests.as_view()),
    path("outgoing_requests/", ListOutgoingRequests.as_view()),
    path("friends/", ListFriends.as_view()),
    path("status/<username>/", UserFriendStatus.as_view()),
    path("confrim_request/", ResponseToFriendRequest.as_view()),
    path("delete_from_friends/", DeleteFromFriends.as_view())
]
