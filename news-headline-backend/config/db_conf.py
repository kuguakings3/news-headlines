import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import async_sessionmaker,AsyncSession,create_async_engine

# 加载 backend 根目录下的 .env（本地开发用，不提交到仓库）
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

#数据库URL：优先读 DATABASE_URL，没有则用分项环境变量拼装
ASYNC_DATABASE_URL = os.getenv("DATABASE_URL") or (
    "mysql+aiomysql://{user}:{password}@{host}:{port}/{db}?charset=utf8".format(
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "3306"),
        db=os.getenv("DB_NAME", "news_app"),
    )
)

# 创建异步引擎
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo = True, # 输出SQL日志
    pool_size = 10, # 设置连接池中保持的持久连接数
    max_overflow = 20, # 设置连接池中允许创建的额外链接数
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind = async_engine,
    class_ = AsyncSession,
    expire_on_commit = False,
)

# 依赖项，用于获取数据库会话
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

