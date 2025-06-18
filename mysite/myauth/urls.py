from django.contrib.auth.views import LoginView
from django.urls import path

from .views import *

app_name = "myauth"



urlpatterns = [
    path("login/",
         LoginView.as_view(
         template_name="myauth/login.html",
         redirect_authenticated_user=True),
         name="login"),
    path("logout/", MyLogoutPage.as_view(), name="logout"),
    path("cookie/get/", get_cookie_view, name="get_cookie"),
    path("cookie/set/", set_cookie_view, name="set_cookie"),
    path("session/get/", get_session_view, name="get_session"),
    path("session/set/", set_session_view, name="set_session"),
    path("about-me/", AboutMeView.as_view(), name="about-me"),
    path("register/", RegisterView.as_view(), name="register"),
    path('users/', UsersListView.as_view(), name='users-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('users/<int:pk>/avatar/', AvatarUpdateView.as_view(), name='avatar-update'),
]

