import json
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import models, transaction
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import RegisterForm, CreateBoardForm, JoinBoardForm
from .models import Board, BoardMember, List, Card
from .permissions import (
    require_member,
    can_manage_roles,
    can_manage_lists,
    can_manage_cards,
    can_read,
)

def _forbidden(msg="forbidden"):
    return HttpResponseForbidden(msg)

def register_view(request):
    if request.user.is_authenticated:
        return redirect("board:home")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("board:home")
    else:
        form = RegisterForm()

    return render(request, "board/register.html", {"form": form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect("board:home")

    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("board:home")
        messages.error(request, "Invalid username or password")

    return render(request, "board/login.html", {})

def logout_view(request):
    logout(request)
    return redirect("board:login")

@login_required
def home(request):
    memberships = BoardMember.objects.select_related("board").filter(user=request.user).order_by("-joined_at")
    create_form = CreateBoardForm()
    join_form = JoinBoardForm()
    return render(
        request,
        "board/home.html",
        {
            "memberships": memberships,
            "create_form": create_form,
            "join_form": join_form,
        },
    )

@login_required
@require_http_methods(["POST"])
def board_create(request):
    body = json.loads(request.body or "{}")
    form = CreateBoardForm(body)
    if not form.is_valid():
        return HttpResponseBadRequest("bad_form")

    name = form.cleaned_data["name"].strip() or "Untitled board"

    join_code = Board.generate_join_code()
    while Board.objects.filter(join_code=join_code).exists():
        join_code = Board.generate_join_code()

    with transaction.atomic():
        b = Board.objects.create(name=name, created_by=request.user, join_code=join_code)
        BoardMember.objects.create(board=b, user=request.user, role=BoardMember.ROLE_ADMIN)

        List.objects.create(board=b, title="To do", position=0)
        List.objects.create(board=b, title="Doing", position=1)
        List.objects.create(board=b, title="Done", position=2)

        Card.objects.create(board=b, list=b.lists.get(position=0), position=0, title="Set up your board", desc="Create lists and add cards.")
        Card.objects.create(board=b, list=b.lists.get(position=0), position=1, title="Drag cards", desc="Reorder within a list or move across lists.")
        Card.objects.create(board=b, list=b.lists.get(position=1), position=0, title="Click a card to edit", desc="Edit title and description in a modal.")
        Card.objects.create(board=b, list=b.lists.get(position=2), position=0, title="Persist to database", desc="Reload the page and your board stays.")

    return JsonResponse({"ok": True, "board_id": b.id})

@login_required
@require_http_methods(["POST"])
def board_join(request):
    body = json.loads(request.body or "{}")
    form = JoinBoardForm(body)
    if not form.is_valid():
        return HttpResponseBadRequest("bad_form")

    code = form.cleaned_data["join_code"].strip()
    b = Board.objects.filter(join_code=code).first()
    if not b:
        return HttpResponseBadRequest("invalid_code")

    BoardMember.objects.get_or_create(
        board=b,
        user=request.user,
        defaults={"role": BoardMember.ROLE_SPECTATOR},
    )

    return JsonResponse({"ok": True, "board_id": b.id})

@login_required
def board_view(request, board_id: int):
    b = get_object_or_404(Board, id=board_id)
    try:
        role = require_member(b, request.user)
    except PermissionError:
        return _forbidden("not_member")

    if not can_read(role):
        return _forbidden()

    q = (request.GET.get("q") or "").strip()

    lists = list(List.objects.filter(board=b).order_by("position", "id"))

    for lst in lists:
        qs = Card.objects.filter(board=b, list=lst).order_by("position", "id")
        if q:
            qs = qs.filter(models.Q(title__icontains=q) | models.Q(desc__icontains=q))
        lst.cards_for_view = list(qs)

    return render(
        request,
        "board/board.html",
        {
            "board": b,
            "role": role,
            "lists": lists,
            "q": q,
        },
    )


@login_required
def members_view(request, board_id: int):
    b = get_object_or_404(Board, id=board_id)
    try:
        role = require_member(b, request.user)
    except PermissionError:
        return _forbidden("not_member")

    members = BoardMember.objects.select_related("user").filter(board=b).order_by("role", "user__username")
    return render(
        request,
        "board/members.html",
        {
            "board": b,
            "role": role,
            "members": members,
        },
    )

@login_required
@require_http_methods(["POST"])
def member_set_role(request, board_id: int):
    b = get_object_or_404(Board, id=board_id)
    try:
        role = require_member(b, request.user)
    except PermissionError:
        return _forbidden("not_member")

    if not can_manage_roles(role):
        return _forbidden("not_admin")

    body = json.loads(request.body or "{}")
    user_id = body.get("user_id")
    new_role = body.get("role")

    valid_roles = dict(BoardMember.ROLE_CHOICES).keys()
    if new_role not in valid_roles:
        return HttpResponseBadRequest("bad_role")

    m = BoardMember.objects.filter(board=b, user_id=user_id).first()
    if not m:
        return HttpResponseBadRequest("member_not_found")

    if m.user_id == b.created_by_id:
        return HttpResponseBadRequest("cannot_change_creator_role")

    m.role = new_role
    m.save(update_fields=["role"])
    return JsonResponse({"ok": True})

@login_required
@require_http_methods(["GET"])
def export_json(request, board_id: int):
    b = get_object_or_404(Board, id=board_id)
    try:
        role = require_member(b, request.user)
    except PermissionError:
        return _forbidden("not_member")

    if not can_read(role):
        return _forbidden()

    lists = list(List.objects.filter(board=b).order_by("position", "id"))
    cards = list(Card.objects.filter(board=b).order_by("list_id", "position", "id"))
    members = list(BoardMember.objects.select_related("user").filter(board=b).order_by("role", "user__username"))

    data = {
        "board": {"id": b.id, "name": b.name, "join_code": b.join_code},
        "members": [{"username": m.user.username, "role": m.role} for m in members],
        "lists": [{"id": l.id, "title": l.title, "position": l.position} for l in lists],
        "cards": [
            {
                "id": c.id,
                "list_id": c.list_id,
                "title": c.title,
                "desc": c.desc,
                "position": c.position,
                "created_at": c.created_at.isoformat(),
            }
            for c in cards
        ],
    }
    return JsonResponse(data, json_dumps_params={"indent": 2})

@login_required
@require_http_methods(["POST"])
def reset_board(request, board_id: int):
    b = get_object_or_404(Board, id=board_id)
    try:
        role = require_member(b, request.user)
    except PermissionError:
        return _forbidden("not_member")

    if role != BoardMember.ROLE_ADMIN:
        return _forbidden("not_admin")

    with transaction.atomic():
        Card.objects.filter(board=b).delete()
        List.objects.filter(board=b).delete()

        List.objects.create(board=b, title="To do", position=0)
        List.objects.create(board=b, title="Doing", position=1)
        List.objects.create(board=b, title="Done", position=2)

    return JsonResponse({"ok": True})

@login_required
@require_http_methods(["POST"])
def list_create(request, board_id: int):
    b = get_object_or_404(Board, id=board_id)
    try:
        role = require_member(b, request.user)
    except PermissionError:
        return _forbidden("not_member")

    if not can_manage_lists(role):
        return _forbidden("no_list_permission")

    body = json.loads(request.body or "{}")
    title = (body.get("title") or "").strip() or "Untitled"

    max_pos = List.objects.filter(board=b).aggregate(models.Max("position")).get("position__max")
    pos = (max_pos + 1) if max_pos is not None else 0

    lst = List.objects.create(board=b, title=title, position=pos)
    return JsonResponse({"ok": True, "id": lst.id})

@login_required
@require_http_methods(["POST"])
def list_rename(request, board_id: int, list_id: int):
    b = get_object_or_404(Board, id=board_id)
    try:
        role = require_member(b, request.user)
    except PermissionError:
        return _forbidden("not_member")

    if not can_manage_lists(role):
        return _forbidden("no_list_permission")

    body = json.loads(request.body or "{}")
    title = (body.get("title") or "").strip() or "Untitled"

    updated = List.objects.filter(board=b, id=list_id).update(title=title)
    if not updated:
        return HttpResponseBadRequest("list_not_found")
    return JsonResponse({"ok": True})

@login_required
@require_http_methods(["POST"])
def list_delete(request, board_id: int, list_id: int):
    b = get_object_or_404(Board, id=board_id)
    try:
        role = require_member(b, request.user)
    except PermissionError:
        return _forbidden("not_member")

    if not can_manage_lists(role):
        return _forbidden("no_list_permission")

    deleted, _ = List.objects.filter(board=b, id=list_id).delete()
    if not deleted:
        return HttpResponseBadRequest("list_not_found")
    return JsonResponse({"ok": True})

@login_required
@require_http_methods(["POST"])
def list_reorder(request, board_id: int):
    b = get_object_or_404(Board, id=board_id)
    try:
        role = require_member(b, request.user)
    except PermissionError:
        return _forbidden("not_member")

    if not can_manage_lists(role):
        return _forbidden("no_list_permission")

    body = json.loads(request.body or "{}")
    order = body.get("order")
    if not isinstance(order, list):
        return HttpResponseBadRequest("bad_order")

    with transaction.atomic():
        for idx, list_id in enumerate(order):
            List.objects.filter(board=b, id=list_id).update(position=idx)

    return JsonResponse({"ok": True})

@login_required
@require_http_methods(["POST"])
def card_create(request, board_id: int):
    b = get_object_or_404(Board, id=board_id)
    try:
        role = require_member(b, request.user)
    except PermissionError:
        return _forbidden("not_member")

    if not can_manage_cards(role):
        return _forbidden("no_card_permission")

    body = json.loads(request.body or "{}")
    list_id = body.get("list_id")
    title = (body.get("title") or "").strip()

    if not list_id or not title:
        return HttpResponseBadRequest("missing_fields")

    lst = List.objects.filter(board=b, id=list_id).first()
    if not lst:
        return HttpResponseBadRequest("list_not_found")

    max_pos = Card.objects.filter(board=b, list=lst).aggregate(models.Max("position")).get("position__max")
    pos = (max_pos + 1) if max_pos is not None else 0

    card = Card.objects.create(
        board=b,
        list=lst,
        title=title,
        desc="",
        tag=Card.TAG_NOT_STARTED,
        position=pos,
    )

    return JsonResponse({"ok": True, "id": card.id})

@login_required
@require_http_methods(["POST"])
def card_update(request, board_id: int, card_id: int):
    b = get_object_or_404(Board, id=board_id)
    try:
        role = require_member(b, request.user)
    except PermissionError:
        return _forbidden("not_member")

    if not can_manage_cards(role):
        return _forbidden("no_card_permission")

    body = json.loads(request.body or "{}")
    title = (body.get("title") or "").trim() if False else (body.get("title") or "").strip()
    desc = (body.get("desc") or "").strip()
    tag = body.get("tag")

    valid_tags = dict(Card.TAG_CHOICES).keys()
    if tag not in valid_tags:
        tag = Card.TAG_NOT_STARTED

    updated = Card.objects.filter(board=b, id=card_id).update(
        title=title or "Untitled",
        desc=desc,
        tag=tag,
    )

    if not updated:
        return HttpResponseBadRequest("card_not_found")
    return JsonResponse({"ok": True})

@login_required
@require_http_methods(["POST"])
def card_delete(request, board_id: int, card_id: int):
    b = get_object_or_404(Board, id=board_id)
    try:
        role = require_member(b, request.user)
    except PermissionError:
        return _forbidden("not_member")

    if not can_manage_cards(role):
        return _forbidden("no_card_permission")

    deleted, _ = Card.objects.filter(board=b, id=card_id).delete()
    if not deleted:
        return HttpResponseBadRequest("card_not_found")
    return JsonResponse({"ok": True})

@login_required
@require_http_methods(["POST"])
def card_move(request, board_id: int):
    b = get_object_or_404(Board, id=board_id)
    try:
        role = require_member(b, request.user)
    except PermissionError:
        return _forbidden("not_member")

    if not can_manage_cards(role):
        return _forbidden("no_card_permission")

    body = json.loads(request.body or "{}")
    card_id = body.get("card_id")
    to_list_id = body.get("to_list_id")
    to_index = body.get("to_index")

    if card_id is None or to_list_id is None or to_index is None:
        return HttpResponseBadRequest("missing_fields")

    card = Card.objects.select_related("list").filter(board=b, id=card_id).first()
    to_list = List.objects.filter(board=b, id=to_list_id).first()
    if not card or not to_list:
        return HttpResponseBadRequest("not_found")

    to_index = int(to_index)

    with transaction.atomic():
        from_list_id = card.list_id

        from_cards = list(Card.objects.filter(board=b, list_id=from_list_id).order_by("position", "id"))
        to_cards = list(Card.objects.filter(board=b, list_id=to_list_id).order_by("position", "id"))

        from_cards = [c for c in from_cards if c.id != card.id]
        if from_list_id == to_list_id:
            to_cards = from_cards

        to_index = max(0, min(to_index, len(to_cards)))
        to_cards.insert(to_index, card)

        if from_list_id != to_list_id:
            for idx, c in enumerate(from_cards):
                Card.objects.filter(board=b, id=c.id).update(position=idx)
            card.list = to_list
            card.save(update_fields=["list"])

        for idx, c in enumerate(to_cards):
            Card.objects.filter(board=b, id=c.id).update(list_id=to_list_id, position=idx)

    return JsonResponse({"ok": True})
