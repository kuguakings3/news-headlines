from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.history import History
from models.news import News


async def add_history(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    record = History(user_id=user_id, news_id=news_id)
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def get_history_list(
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        page_size: int = 20
):
    """浏览历史列表：同一篇新闻只出现一次，保留最后一次浏览时间"""
    # 第一步：把「同一个人看同一篇」的多条记录压成一条，只留最新的 view_time
    sub = (
        select(
            History.news_id.label("news_id"),
            func.max(History.view_time).label("view_time"),
        )
        .where(History.user_id == user_id)
        .group_by(History.news_id)
        .subquery()
    )

    # 总数 = 去重后的新闻篇数
    total = (await db.execute(select(func.count()).select_from(sub))).scalar_one()

    # 第二步：拿这张「新闻ID + 最后浏览时间」的表去 join 新闻表，把标题封面捞出来
    offset = (page - 1) * page_size
    query = (
        select(News, sub.c.view_time)
        .join(sub, sub.c.news_id == News.id)
        .order_by(sub.c.view_time.desc())
        .offset(offset)
        .limit(page_size)
    )
    rows = (await db.execute(query)).all()
    return rows, total


async def delete_by_news(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    """按新闻ID删：把这个人看这篇新闻的所有记录一起删掉"""
    stmt = delete(History).where(History.user_id == user_id, History.news_id == news_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount or 0


async def clear_by_user(
        db: AsyncSession,
        user_id: int
):
    stmt = delete(History).where(History.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount or 0
