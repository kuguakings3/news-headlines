from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class HistoryAddRequest(BaseModel):
    news_id: int = Field(..., alias="newsId")


class HistoryItemResponse(BaseModel):
    """列表里的一条：新闻信息 + 我最后一次看它的时间"""
    id: int
    title: str
    description: Optional[str] = None
    image: Optional[str] = None
    author: Optional[str] = None
    publishTime: datetime
    viewTime: datetime


class HistoryListResponse(BaseModel):
    list: list[HistoryItemResponse]
    total: int
    hasMore: bool
