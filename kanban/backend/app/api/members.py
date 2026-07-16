from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.permissions import get_current_user, require_board
from ..database import get_db
from ..models import BoardMember, User
from ..schemas.board import MemberAdd, MemberOut, MemberUpdate
from ..services import audit_service

router = APIRouter(prefix="/boards/{board_id}/members", tags=["members"])


@router.get("", response_model=list[MemberOut])
def list_members(board_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    board = require_board(db, board_id, user, "reader")
    return board.members


@router.post("", response_model=MemberOut, status_code=201)
def add_member(board_id: int, data: MemberAdd, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_board(db, board_id, user, "owner")
    target = db.execute(select(User).where(User.login == data.login)).scalar_one_or_none()
    if target is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Пользователь с таким логином не найден")
    exists = db.execute(
        select(BoardMember).where(BoardMember.board_id == board_id, BoardMember.user_id == target.id)
    ).scalar_one_or_none()
    if exists:
        raise HTTPException(status.HTTP_409_CONFLICT, "Пользователь уже участник доски")
    member = BoardMember(board_id=board_id, user_id=target.id, role=data.role)
    db.add(member)
    audit_service.log(db, board_id=board_id, user_id=user.id, entity="member", entity_id=target.id, action="create", payload={"login": data.login, "role": data.role})
    db.commit()
    db.refresh(member)
    return member


@router.patch("/{member_user_id}", response_model=MemberOut)
def update_member(board_id: int, member_user_id: int, data: MemberUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    board = require_board(db, board_id, user, "owner")
    if member_user_id == board.owner_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Роль владельца доски изменить нельзя")
    member = db.execute(
        select(BoardMember).where(BoardMember.board_id == board_id, BoardMember.user_id == member_user_id)
    ).scalar_one_or_none()
    if member is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Участник не найден")
    member.role = data.role
    audit_service.log(db, board_id=board_id, user_id=user.id, entity="member", entity_id=member_user_id, action="update", payload={"role": data.role})
    db.commit()
    db.refresh(member)
    return member


@router.delete("/{member_user_id}", status_code=204)
def remove_member(board_id: int, member_user_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    board = require_board(db, board_id, user, "owner")
    if member_user_id == board.owner_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Владельца доски исключить нельзя")
    member = db.execute(
        select(BoardMember).where(BoardMember.board_id == board_id, BoardMember.user_id == member_user_id)
    ).scalar_one_or_none()
    if member is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Участник не найден")
    db.delete(member)
    audit_service.log(db, board_id=board_id, user_id=user.id, entity="member", entity_id=member_user_id, action="delete")
    db.commit()
