"""Начальная схема: users, boards, board_members, columns, cards, comments, audit_log

Revision ID: 0001
Revises:
"""
import sqlalchemy as sa
from alembic import op

# BigInteger на PostgreSQL (BIGSERIAL), Integer на SQLite (нужен для rowid-автоинкремента при dev-запуске)
PK_TYPE = sa.BigInteger().with_variant(sa.Integer, "sqlite")

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

board_role = sa.Enum("reader", "writer", "owner", name="board_role")


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", PK_TYPE, primary_key=True),
        sa.Column("login", sa.String(64), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "boards",
        sa.Column("id", PK_TYPE, primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("owner_id", PK_TYPE, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "board_members",
        sa.Column("board_id", PK_TYPE, sa.ForeignKey("boards.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("user_id", PK_TYPE, sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("role", board_role, nullable=False, server_default="reader"),
        sa.Column("added_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_board_members_user", "board_members", ["user_id"])
    op.create_table(
        "columns",
        sa.Column("id", PK_TYPE, primary_key=True),
        sa.Column("board_id", PK_TYPE, sa.ForeignKey("boards.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("position", sa.Integer, nullable=False),
    )
    op.create_index("idx_columns_board", "columns", ["board_id", "position"])
    op.create_table(
        "cards",
        sa.Column("id", PK_TYPE, primary_key=True),
        sa.Column("column_id", PK_TYPE, sa.ForeignKey("columns.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("assignee_id", PK_TYPE, sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("deadline", sa.DateTime(timezone=True)),
        sa.Column("position", sa.Numeric(20, 10), nullable=False),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_cards_column", "cards", ["column_id", "position"])
    op.create_index("idx_cards_assignee", "cards", ["assignee_id"])
    op.create_index("idx_cards_deadline", "cards", ["deadline"])
    op.create_table(
        "comments",
        sa.Column("id", PK_TYPE, primary_key=True),
        sa.Column("card_id", PK_TYPE, sa.ForeignKey("cards.id", ondelete="CASCADE"), nullable=False),
        sa.Column("author_id", PK_TYPE, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_comments_card", "comments", ["card_id", "created_at"])
    op.create_table(
        "audit_log",
        sa.Column("id", PK_TYPE, primary_key=True),
        sa.Column("board_id", PK_TYPE, sa.ForeignKey("boards.id", ondelete="CASCADE")),
        sa.Column("user_id", PK_TYPE, sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("entity", sa.String(32), nullable=False),
        sa.Column("entity_id", sa.BigInteger),
        sa.Column("action", sa.String(32), nullable=False),
        sa.Column("payload", sa.JSON().with_variant(sa.dialects.postgresql.JSONB(), "postgresql")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_audit_board_time", "audit_log", ["board_id", "created_at"])


def downgrade() -> None:
    for t in ("audit_log", "comments", "cards", "columns", "board_members", "boards", "users"):
        op.drop_table(t)
    board_role.drop(op.get_bind(), checkfirst=True)
