from fastapi import Header, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette import status

from config.db_conf import get_db
from crud import users


# 整合 根据token 查询用户
async def get_current_user(
        authorization:str = Header(...,alias="authorization"),
        db:AsyncSession = Depends(get_db)
):
    # 兼容 "Bearer xxx" 和裸 token 两种写法（前端当前传的是裸 token）
    token = authorization.replace('Bearer', '').strip()
    user = await users.get_user_by_token(db,token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid credentials")

    return user

