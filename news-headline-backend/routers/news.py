
from fastapi import APIRouter,Depends,HTTPException
from fastapi.params import Query
from sqlalchemy import null
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud import news

# 创建APIrouter 实例
router = APIRouter(prefix="/api/news",tags=["news"])

# 接口实现流程
# 1.模块化路由 -> API接口规范文档
# 2.定义模型类 ->数据库表
# 3.在crud 文件夹里创建文件，封装操作数据库的方法
# 4.在路由处理函数里面crud封装好的方法，响应结果


@router.get("/categories")# 获取新闻分类
async def get_categories(
        skip: int = 0, # 跳过
        limit: int = 100, # 限制
        db:AsyncSession = Depends(get_db) # 依赖注入
):
    # 先获取数据库的新闻分类->定义模型类->封装查询数据库的方法
    # 调用crud文件夹里的news.py文件里的get_categories方法，获取新闻分类
    categories = await news.get_categories(db,skip, limit)
    return{
        "code":200,
        "message":"success",
        "data":categories # 展示详细的新闻分类信息
    }

@router.get("/list")# 获取新闻列表
async def get_news_list(
        category_id: int = Query(...,alias="categoryId"), # 分类id
        page:int = 1, # 页码
        page_size:int = Query(10,alias="pageSize",le=100), # 页大小
        db:AsyncSession = Depends(get_db)
):
    # 处理分页规则->查询新闻列表->计算总量->计算是否含有更多
    offset = (page-1)*page_size # 跳过
    news_list = await news.get_news_list(
        db,
        category_id,
        offset,
        page_size) # 执行查询新闻列表
    # 计算总量
    total = await news.get_news_count(db,category_id)
    # 是否还有更多（跳过的+当前页有的）<总量）
    has_more = (offset+ len(news_list))<total # 计算是否还有更多
    return{
        "code":200,
        "message":"success",
        "data":{
            "list":news_list,
            "total":total,
            "has_more":has_more,
        }

    }

@router.get("/detail")# 获取新闻详情->查询新闻详情->检查新闻是否存在->更新新闻浏览量->检查更新结果->获取相关新闻->返回结果
async def get_news_detail(
        # 查询参数
    news_id: int= Query(...,alias="id"),db:AsyncSession = Depends(get_db)):

    # 获取新闻详情
    news_detail = await news.get_news_detail(db,news_id)

    # 检查新闻是否存在
    if not news_detail:
        raise HTTPException(status_code=404,detail="新闻不存在")


    # 更新新闻浏览量
    views_res = await news.increase_news_view(db,news_id)
    # 检查更新结果
    if not views_res:
        raise HTTPException(status_code=500,detail="更新浏览量失败")
    # 获取相关新闻
    related_news = await news.get_related_news(db,news_detail.category_id,news_detail.id)
    # 返回结果
    return{
      "code": 200,
      "message": "success",
      "data": {
        "id":news_detail.id,
        "title": news_detail.title,
        "content": news_detail.content,
        "image": news_detail.image,
        "author": news_detail.author,
        "publishTime": news_detail.publish_time,
        "categoryId": news_detail.category_id,
        "views": news_detail.views,
        "relatedNews": related_news
      }
    }


