from .models import BoardMember

def get_role(board, user):
    if not user.is_authenticated:
        return None
    m = BoardMember.objects.filter(board=board, user=user).first()
    return m.role if m else None

def require_member(board, user):
    role = get_role(board, user)
    if not role:
        raise PermissionError("not_member")
    return role

def can_read(role):
    return role in ["admin", "mentor", "student", "spectator"]

def can_manage_roles(role):
    return role == "admin"

def can_manage_lists(role):
    return role in ["admin", "mentor"]

def can_manage_cards(role):
    return role in ["admin", "mentor", "student"]
