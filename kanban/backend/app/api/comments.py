from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.permissions import get_current_user, require_board
from ..database import get_db
from ..models import Card, Column, Comment, User
from ..schemas.comment import CommentCreate, CommentOut
from ..services import audit_service

router = APIRouter(tags=["comments"])


def _board_of_card(db: Session, card_id: int) -> tuple[Card, int]:
    card = db.get(Card, card_id)
    if card is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Карточка не найдена")
    return card, db.get(Column, card.column_id).board_id


@router.get("/cards/{card_id}/comments", response_model=list[CommentOut])
def list_comments(card_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    card, board_id = _board_of_card(db, card_id)
    require_board(db, board_id, user, "reader")
    return card.comments


@router.post("/cards/{card_id}/comments", response_model=CommentOut, status_code=201)
def add_comment(card_id: int, data: CommentCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    card, board_id = _board_of_card(db, card_id)
    require_board(db, board_id, user, "writer")
    comment = Comment(card_id=card_id, author_id=user.id, body=data.body)
    db.add(comment)
    audit_service.log(db, board_id=board_id, user_id=user.id, entity="comment", entity_id=card_id, action="create")
    db.commit()
    db.refresh(comment)
    return comment


@router.delete("/comments/{comment_id}", status_code=204)
def delete_comment(comment_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    comment = db.get(Comment, comment_id)
    if comment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Комментарий не найден")
    card, board_id = _board_of_card(db, comment.card_id)
    require_board(db, board_id, user, "writer")
    if comment.author_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Удалять можно только свои комментарии")
    db.delete(comment)
    audit_service.log(db, board_id=board_id, user_id=user.id, entity="comment", entity_id=comment_id, action="delete")
    db.commit()
