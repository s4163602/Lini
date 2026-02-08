import secrets
from django.conf import settings
from django.db import models

class Board(models.Model):
    name = models.CharField(max_length=120, default="Untitled board")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_boards",
    )
    join_code = models.CharField(max_length=16, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def generate_join_code() -> str:
        code = secrets.token_urlsafe(9).replace("-", "").replace("_", "")
        return code[:16]

class BoardMember(models.Model):
    ROLE_ADMIN = "admin"
    ROLE_MENTOR = "mentor"
    ROLE_STUDENT = "student"
    ROLE_SPECTATOR = "spectator"

    ROLE_CHOICES = [
        (ROLE_ADMIN, "Admin"),
        (ROLE_MENTOR, "Mentor"),
        (ROLE_STUDENT, "Student"),
        (ROLE_SPECTATOR, "Spectator"),
    ]

    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="board_memberships")
    role = models.CharField(max_length=12, choices=ROLE_CHOICES, default=ROLE_SPECTATOR)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("board", "user")]

    def __str__(self) -> str:
        return f"{self.board_id}:{self.user_id}:{self.role}"

class List(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="lists")
    title = models.CharField(max_length=120, default="Untitled")
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position", "id"]

    def __str__(self) -> str:
        return self.title

class Card(models.Model):
    TAG_NOT_STARTED = "not_started"
    TAG_IN_PROGRESS = "in_progress"
    TAG_FINISHED = "finished"

    TAG_CHOICES = [
        (TAG_NOT_STARTED, "Not started"),
        (TAG_IN_PROGRESS, "In progress"),
        (TAG_FINISHED, "Finished"),
    ]

    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="cards")
    list = models.ForeignKey(List, on_delete=models.CASCADE, related_name="cards")
    title = models.CharField(max_length=200, default="Untitled")
    desc = models.TextField(blank=True, default="")
    tag = models.CharField(
        max_length=20,
        choices=TAG_CHOICES,
        default=TAG_NOT_STARTED,
    )
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["position", "id"]

    def __str__(self):
        return self.title

