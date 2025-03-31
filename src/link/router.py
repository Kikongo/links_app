from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
import time
from database import get_async_session
from .models import link
from .schemas import ShortenRequest
from fastapi_cache.decorator import cache
from datetime import datetime
import random
import string

router = APIRouter(
    prefix="/link",
    tags=["Link"]
)


@router.get("/long")
@cache(expire=60)
async def get_long():
    time.sleep(5)
    return "hello"

# Generate unique short code
def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@router.post("/links/shorten")
async def shorten_url(request: ShortenRequest, db: AsyncSession = Depends(get_async_session)):
    short_code = request.custom_alias if request.custom_alias else generate_short_code()
    
    result = await db.execute(select(link).where(link.c.short_code == short_code))
    if result.scalar():
        raise HTTPException(status_code=400, detail="Short code already exists")
    
    new_link = {
        "original_url": str(request.original_url),
        "short_code": short_code,
        "expires_at": request.expires_at,
    }
    await db.execute(link.insert().values(new_link))
    await db.commit()
    return {"short_url": f"http://localhost/{short_code}"}

@router.get("/{short_code}")
async def redirect(short_code: str, db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(link).where(link.c.short_code == short_code))
    link_data = result.fetchone()
    if not link_data or (link_data.expires_at and link_data.expires_at < datetime.utcnow()):
        raise HTTPException(status_code=404, detail="Link not found or expired")
    await db.execute(
        link.update().where(link.c.short_code == short_code).values(
            visit_count=link.c.visit_count + 1, last_visited=datetime.utcnow()
        )
    )
    await db.commit()
    return {"redirect": link_data.original_url}

@router.get("/links/{short_code}/stats")
async def get_link_stats(short_code: str, db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(link).where(link.c.short_code == short_code))
    link_data = result.fetchone()
    if not link_data:
        raise HTTPException(status_code=404, detail="Link not found")
    return {
        "original_url": link_data.original_url,
        "created_at": link_data.created_at,
        "visit_count": link_data.visit_count,
        "last_visited": link_data.last_visited
    }

@router.get("/links/search")
async def search_link(original_url: str, db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(link).where(link.c.original_url == original_url))
    link_data = result.fetchone()
    if not link_data:
        raise HTTPException(status_code=404, detail="Link not found")
    return {"short_url": f"http://localhost/{link_data.short_code}"}

@router.delete("/links/{short_code}")
async def delete_link(short_code: str, db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(link).where(link.c.short_code == short_code))
    link_data = result.fetchone()
    if not link_data:
        raise HTTPException(status_code=404, detail="Link not found")
    await db.execute(link.delete().where(link.c.short_code == short_code))
    await db.commit()
    return {"message": "Link deleted successfully"}