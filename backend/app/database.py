from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# This is a DIRECT connection to Supabase Postgres (port 5432), so we
# manage our own connection pool here via SQLAlchemy — that's the
# "direct connection pooling" you asked for, as opposed to routing
# through Supabase's pgbouncer (transaction pooler on 6543).
#
# pool_pre_ping: checks a connection is alive before handing it out
#                (guards against Supabase closing idle connections).
# pool_recycle: recycle connections every 30 min so none go stale.
engine = create_async_engine(
    settings.database_url,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_pre_ping=True,
    pool_recycle=1800,
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session