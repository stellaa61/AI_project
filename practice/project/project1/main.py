from contextlib import asynccontextmanager

from fastapi import FastAPI

from database.connection import engine
from database.orm import Base

from routers.user import router as user_router
from routers.prediction import router as prediction_router


@asynccontextmanager
async def lifespan(_):
    # 서버 시작 전, 테이블 자동 생성
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

# lifespan = 시작과 종료 라이프 사이클을 정리
app = FastAPI(lifespan=lifespan)
app.include_router(user_router)
app.include_router(prediction_router)


# 토큰   eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwiZXhwIjoxNzczMjgyODYyfQ.t1aOpyFHEkJhx8A6xU5S90yer80gaDZv9ybIbz57cKU
