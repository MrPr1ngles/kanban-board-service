from sqlalchemy import BigInteger, Integer

# В PostgreSQL — BIGINT, в SQLite (для локальных тестов) — INTEGER с автоинкрементом
PK = BigInteger().with_variant(Integer, "sqlite")
FK = BigInteger().with_variant(Integer, "sqlite")
