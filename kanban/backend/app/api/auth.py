from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.security import create_token, hash_password, verify_password
from ..database import get_db
from ..models import User
from ..schemas.auth import Credentials, TokenOut, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=201)
def register(data: Credentials, db: Session = Depends(get_db)):
    exists = db.execute(select(User).where(User.login == data.login)).scalar_one_or_none()
    if exists:
        raise HTTPException(status.HTTP_409_CONFLICT, "Логин уже занят")
    user = User(login=data.login, password_hash=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenOut)
def login(data: Credentials, db: Session = Depends(get_db)):
    user = db.execute(select(User).where(User.login == data.login)).scalar_one_or_none()
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Неверный логин или пароль")
    return TokenOut(auth_token=create_token(user.id))
