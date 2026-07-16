"""Наполнение БД демо-данными: python -m scripts.seed"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.security import hash_password
from app.database import Base, SessionLocal, engine
from app.models import Board, BoardMember, Card, Column, Comment, User


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if db.query(User).count() > 0:
        print("БД уже наполнена, пропускаю")
        return

    users = {}
    for login in ("alice", "bob", "carol"):
        u = User(login=login, password_hash=hash_password("password123"))
        db.add(u)
        users[login] = u
    db.flush()

    board = Board(title="Новая доска", description="Демо-доска из презентации", owner_id=users["alice"].id)
    db.add(board)
    db.flush()
    db.add_all([
        BoardMember(board_id=board.id, user_id=users["alice"].id, role="owner"),
        BoardMember(board_id=board.id, user_id=users["bob"].id, role="writer"),
        BoardMember(board_id=board.id, user_id=users["carol"].id, role="reader"),
    ])

    cols = [Column(board_id=board.id, title=t, position=i + 1) for i, t in enumerate(("Очередь", "В работе", "Готово"))]
    db.add_all(cols)
    db.flush()

    cards = [
        Card(column_id=cols[0].id, title="Классно поспать", position=1024),
        Card(column_id=cols[0].id, title="Вкусно поесть", position=2048),
        Card(column_id=cols[1].id, title="Желательно поработать", position=1024, assignee_id=users["bob"].id),
        Card(column_id=cols[2].id, title="Сделать презентацию для студентов", position=1024, assignee_id=users["alice"].id),
    ]
    db.add_all(cards)
    db.flush()
    db.add(Comment(card_id=cards[2].id, author_id=users["alice"].id, body="Не забудь про дедлайн!"))
    db.commit()
    print("Демо-данные созданы. Логины: alice / bob / carol, пароль: password123")


if __name__ == "__main__":
    run()
