from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import audit, auth, boards, cards, columns, comments, members
from .database import Base, engine

app = FastAPI(title="Kanban board API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Для продакшена схема управляется Alembic-миграциями; create_all — подстраховка для dev
Base.metadata.create_all(bind=engine)

for router in (auth.router, boards.router, members.router, columns.router, cards.router, comments.router, audit.router):
    app.include_router(router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}
