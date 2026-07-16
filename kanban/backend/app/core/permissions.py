import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Board, BoardMember, User
from .security import decode_token

bearer = HTTPBearer(auto_error=False)

# RBAC: иерархия ролей на уровне доски
ROLE_ORDER = {"reader": 1, "writer": 2, "owner": 3}


def get_current_user(
    cred: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if cred is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Не передан токен авторизации")
    try:
        user_id = decode_token(cred.credentials)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Срок действия токена истёк")
    except jwt.InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Некорректный токен")
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Пользователь не найден")
    return user


def get_role(db: Session, board_id: int, user_id: int) -> str | None:
    member = db.execute(
        select(BoardMember).where(BoardMember.board_id == board_id, BoardMember.user_id == user_id)
    ).scalar_one_or_none()
    return member.role if member else None


def require_board(db: Session, board_id: int, user: User, min_role: str) -> Board:
    """Возвращает доску, если у пользователя есть роль не ниже min_role, иначе 403/404."""
    board = db.get(Board, board_id)
    if board is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Доска не найдена")
    role = get_role(db, board_id, user.id)
    if role is None:
        # принцип минимальных привилегий: чужая доска неотличима от несуществующей
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Доска не найдена")
    if ROLE_ORDER[role] < ROLE_ORDER[min_role]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Недостаточно прав")
    return board
