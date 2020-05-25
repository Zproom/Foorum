from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("following", views.view_following, name="view-following"),
    path("<str:username>", views.view_user, name="view-user"),
    path("board/<int:board_id>", views.view_board, name="view-board"),
    path(
        "board/post/<int:post_id>",
        views.view_comments,
        name="view-comments"),

    # API Routes
    path("forum/<int:post_id>", views.post, name="post"),
    path("forum/<str:username>", views.user, name="user"),
    path(
        "forum/comment/compose/<int:post_id>",
        views.compose_comment,
        name="compose_comment")
]
