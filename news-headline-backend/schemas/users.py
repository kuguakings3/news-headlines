from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class UserRequest(BaseModel):
    username: str
    password: str


# user_infc 对应的类:基础类 + Info类（ID，用户名）
class UserInfoBase(BaseModel):
    """
    用户信息基础数据模型
    """
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")


class UserInfoResponse(UserInfoBase):
    id: int
    username: str

    model_config = ConfigDict(
        from_attributes=True,
    )

# data 数据类型
class UserAuthResponse(BaseModel):
    token: str
    userInfo: UserInfoResponse  # 前端读取 response.data.data.userInfo，保持驼峰一致

    #模型类配置
    model_config = ConfigDict(
        populate_by_name=True,# alias,字段名兼容
        from_attributes=True,# 从ORM属性中获取数据
    )

# 更新用户信息的模型类
class UserUpdateRequest(BaseModel):
    nickname: str = None  # 昵称
    avatar: str = None
    gender: str = None
    bio: str = None
    phone:str = None

class UserChangePasswordRequest(BaseModel):
    old_password: str =  Field(...,description="旧密码",alias="oldPassword")
    new_password: str = Field(...,min_length=6,description="新密码",alias="newPassword")
