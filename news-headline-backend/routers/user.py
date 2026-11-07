from email import message

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_conf import get_db
from crud import users
from models.users import User
from schemas.users import UserRequest, UserAuthResponse, UserInfoResponse, UserUpdateRequest, UserChangePasswordRequest
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/user",tags=["users"])

@router.post("/register")
async def register(user_date:UserRequest,db:AsyncSession = Depends(get_db)): # 用户信息和db
    # 注册用户：验证用户是否存在->创建用户->生成token->响应结果
    existing_user = await users.get_user_by_username(db,user_date.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User with that username already exists")
    user = await users.create_user(db,user_date)
    token = await users.create_token(db,user.id)

    # return {
    #     "code": 200,
    #     "message": "success",
    #     "data": {
    #         "token":token,
    #         "userInfo":{
    #             "id":user.id,
    #             "username":user.username,
    #             "bio":user.bio,
    #             "avatar":user.avatar,
    #         }
    #     }
    # }
    response_data = UserAuthResponse(token=token,userInfo=UserInfoResponse.model_validate(user))
    return success_response(message = "注册成功",data =response_data)

@router.post("/login")
async def login(user_date:UserRequest,db:AsyncSession = Depends(get_db)):
    # 登录逻辑：验证用户是否存在->验证密码->生成token->响应结果
    user = await users.authenticate_user(db,user_date.username,user_date.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid credentials")
    token = await users.create_token(db,user.id)
    response_data = UserAuthResponse(token=token,userInfo=UserInfoResponse.model_validate(user))
    return success_response(message = "登录成功",data = response_data)


# 查token 查用户->封装crud->功能整合成一个工具函数->路由导入使用
@router.get("/info")
async def get_user_info(
        # Authorization: str = Header(None),
        # db: AsyncSession = Depends(get_db)
        user:User = Depends(get_current_user)
):
    # 根据前端传来的 token（Authorization 头，无 Bearer 前缀）反查用户
    # if not Authorization:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录")
    # result = await db.execute(select(UserToken).where(UserToken.token == Authorization))
    # user_token = result.scalars().one_or_none()
    # if not user_token:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效令牌")
    # user = await db.get(User, user_token.user_id)
    # if not user:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")

    return success_response(message = "获取信息成功", data = UserInfoResponse.model_validate(user))

# 修改用户信息：验证token ->更新(用户输入数据 put提交->请求体参数 ->定义Pydantic模型类)->响应结果
# 参数 ：用户输入的+验证token的+db（调用更新的方法）
@router.put("/update")
async def update_user_info(
        user_date:UserUpdateRequest,
        user:User = Depends(get_current_user),
        db:AsyncSession = Depends(get_db)
):
    user = await users.update_user(db,user.username,user_date)
    return success_response(message="更新用户成功",data = UserInfoResponse.model_validate(user))

@router.put("/password")
async def update_password(
        password_data : UserChangePasswordRequest,
        user:User = Depends(get_current_user),
        db:AsyncSession = Depends(get_db)
):
    res_change_pwd = await users.change_password(db,user,password_data.old_password,password_data.new_password)
    if not res_change_pwd:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="修改密码失败")
    return success_response(message="修改密码成功")