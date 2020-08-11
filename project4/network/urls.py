
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("index/<str:message>", views.index, name="index_message"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_post", views.create_post, name="create_post"),
    path("follow", views.follow, name="follow"),
    path("like", views.like, name="like"),
    path("edit_post", views.edit_post, name="edit_post")
]
