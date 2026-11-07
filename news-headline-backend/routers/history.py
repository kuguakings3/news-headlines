from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud import history
from models.users import User
from schemas.history import HistoryAddRequest, HistoryItemResponse, HistoryListResponse
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/history", tags=["history"])


@router.post("/add")
async def add_history(
        data: HistoryAddRequest,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await history.add_history(db, user.id, data.news_id)
    return success_response(message="添加成功", data=result)


@router.get("/list")
async def get_history_list(
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100, alias="pageSize"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    rows, total = await history.get_history_list(db, user.id, page, page_size)

    items = [
        HistoryItemResponse(
            id=news.id,
            title=news.title,
            description=news.description,
            image=news.image,
            author=news.author,
            publishTime=news.publish_time,
            viewTime=view_time,
        )
        for news, view_time in rows
    ]

    data = HistoryListResponse(
        list=items,
        total=total,
        hasMore=total > page * page_size,
    )
    return success_response(message="获取浏览历史成功", data=data)


@router.delete("/delete/{news_id}")
async def delete_history(
        news_id: int,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    count = await history.delete_by_news(db, user.id, news_id)
    return success_response(message=f"已删除{count}条浏览记录")


@router.delete("/clear")
async def clear_history(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    count = await history.clear_by_user(db, user.id)
    return success_response(message=f"已清空{count}条浏览记录")
