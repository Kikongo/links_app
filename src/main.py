from fastapi import FastAPI, Depends, HTTPException
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from auth.users import auth_backend, current_active_user, fastapi_users
from auth.schemas import UserCreate, UserRead #, UserUpdate
from auth.db import User, create_db_and_tables
from link.router import router as link_router
from tasks.router import router as tasks_router
from redis import asyncio as aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

import uvicorn


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    # await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(link_router)

app.include_router(tasks_router)


@app.get("/protected-route")
def protected_route(user: User = Depends(current_active_user)):
    return f"Hello, {user.email}"


@app.get("/unprotected-route")
def unprotected_route():
    return f"Hello, anonym"


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, host="0.0.0.0", log_level="info")
