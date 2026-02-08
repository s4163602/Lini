from django.urls import path
from . import views

app_name = "board"

urlpatterns = [
    path("", views.home, name="home"),

    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("boards/<int:board_id>/", views.board_view, name="board_view"),
    path("boards/<int:board_id>/members/", views.members_view, name="members_view"),

    path("api/boards/create/", views.board_create, name="board_create"),
    path("api/boards/join/", views.board_join, name="board_join"),
    path("api/boards/<int:board_id>/role/", views.member_set_role, name="member_set_role"),

    path("api/boards/<int:board_id>/export/", views.export_json, name="export_json"),
    path("api/boards/<int:board_id>/reset/", views.reset_board, name="reset_board"),

    path("api/boards/<int:board_id>/list/create/", views.list_create, name="list_create"),
    path("api/boards/<int:board_id>/list/<int:list_id>/rename/", views.list_rename, name="list_rename"),
    path("api/boards/<int:board_id>/list/<int:list_id>/delete/", views.list_delete, name="list_delete"),
    path("api/boards/<int:board_id>/list/reorder/", views.list_reorder, name="list_reorder"),

    path("api/boards/<int:board_id>/card/create/", views.card_create, name="card_create"),
    path("api/boards/<int:board_id>/card/<int:card_id>/update/", views.card_update, name="card_update"),
    path("api/boards/<int:board_id>/card/<int:card_id>/delete/", views.card_delete, name="card_delete"),
    path("api/boards/<int:board_id>/card/move/", views.card_move, name="card_move"),
]
