from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from ..config import settings

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    # bcrypt: соль встроена в хэш, в базе только результат hash()
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(hours=settings.jwt_ttl_hours),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


def decode_token(token: str) -> int:
    payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
    return int(payload["sub"])
