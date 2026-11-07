from fastapi import FastAPI
from routers import news, user, favorite, history
# 1.5 CORS解决跨域请求问题（导包）
from fastapi.middleware.cors import CORSMiddleware

from utils.exception_handlers import register_exception_handlers

app = FastAPI()

# 注册异常处理器
register_exception_handlers(app)

app.add_middleware(# 解决CORS问题
    CORSMiddleware,
    allow_origins=["*"], # 允许的源，实际生产只能放运行的前端
    allow_credentials=True, # 允许携带cookie
    allow_methods=["*"], # 允许的请求方法
    allow_headers=["*"], # 允许的请求头
)
@app.get("/")
async def root():
    return {"message": "Hello World"}

# 挂载路由/注册路由
app.include_router(news.router)
app.include_router(user.router)

app.include_router(favorite.router)

app.include_router(history.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
