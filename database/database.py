from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

user = "danielmoreno"
password = "da.ni.el."
host = "localhost"
database = "tasks"
DATABASE_URL = f"postgresql+asyncpg://{user}:{password}@{host}/{database}"

# Create the engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create a configured "Session" class
async_session = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)

# Create a base class for declarative models
Base = declarative_base()

# Dependency to get the session
async def get_db():
    async with async_session() as session:
        yield session