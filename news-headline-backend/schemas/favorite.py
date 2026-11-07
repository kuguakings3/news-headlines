from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from schemas.base import NewsItemBase


class FavoriteCheckResponse(BaseModel):
    is_favorite: bool = Field(..., description="是否收藏了该新闻",alias="isFavorite")

class FavoriteAddRequest(BaseModel):
    news_id :int = Field(...,alias="newsId")

# 规划两个类：一个是新闻模型类+收藏的模型类
class FavoriteNewsItemResponse(NewsItemBase):
    favorite_id:int = Field(...,alias="favoriteId")
    favorite_time: datetime = Field(...,alias="favoriteTime", description="收藏时间")
    model_config = ConfigDict(
            populate_by_name=True,
            from_attributes=True

        )

# 收藏列表接口响应的模型类
class FavoriteListResponse(BaseModel):
    list:list[FavoriteNewsItemResponse]
    total:int
    has_more:bool = Field(...,alias="hasMore")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True

    )