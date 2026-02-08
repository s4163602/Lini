from django.contrib import admin
from .models import Board, BoardMember, List, Card

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_by", "join_code", "created_at")
    search_fields = ("name", "join_code", "created_by__username")

@admin.register(BoardMember)
class BoardMemberAdmin(admin.ModelAdmin):
    list_display = ("id", "board", "user", "role", "joined_at")
    list_filter = ("role",)
    search_fields = ("board__name", "user__username")

@admin.register(List)
class ListAdmin(admin.ModelAdmin):
    list_display = ("id", "board", "title", "position")
    list_filter = ("board",)

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ("id", "board", "list", "title", "position", "created_at")
    list_filter = ("board", "list")
    search_fields = ("title", "desc")
