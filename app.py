from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, HttpUrl
from datetime import datetime, timedelta
from sqlalchemy import Column, String, Integer, DateTime, Boolean
from sqlalchemy.orm import Session
from database import Base, engine, get_db
import random
import string
import uvicorn

app = FastAPI()

# Database model
class LinkTest(Base):
    __table_args__ = {'extend_existing': True}
    __tablename__ = "linkstest"
    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, nullable=False)
    short_code = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    visit_count = Column(Integer, default=0)
    last_visited = Column(DateTime, nullable=True)

Base.metadata.create_all(bind=engine)

# Request model
class ShortenRequest(BaseModel):
    original_url: HttpUrl
    custom_alias: str | None = None
    expires_at: datetime | None = None

# Generate unique short code
def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.post("/links/shorten")
def shorten_url(request: ShortenRequest, db: Session = Depends(get_db)):
    short_code = request.custom_alias if request.custom_alias else generate_short_code()
    
    if db.query(LinkTest).filter(LinkTest.short_code == short_code).first():
        raise HTTPException(status_code=400, detail="Short code already exists")
    
    new_link = LinkTest(
        original_url=str(request.original_url),
        short_code=short_code,
        expires_at=request.expires_at
    )
    db.add(new_link)
    db.commit()
    return {"short_url": f"http://localhost/{short_code}"}

@app.get("/{short_code}")
def redirect(short_code: str, db: Session = Depends(get_db)):
    link = db.query(LinkTest).filter(LinkTest.short_code == short_code).first()
    if not link or (link.expires_at and link.expires_at < datetime.utcnow()):
        raise HTTPException(status_code=404, detail="Link not found or expired")
    link.visit_count += 1
    link.last_visited = datetime.utcnow()
    db.commit()
    return {"redirect": link.original_url}

@app.get("/links/{short_code}/stats")
def get_link_stats(short_code: str, db: Session = Depends(get_db)):
    link = db.query(LinkTest).filter(LinkTest.short_code == short_code).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return {
        "original_url": link.original_url,
        "created_at": link.created_at,
        "visit_count": link.visit_count,
        "last_visited": link.last_visited
    }

@app.get("/links/search")
def search_link(original_url: str, db: Session = Depends(get_db)):
    link = db.query(LinkTest).filter(LinkTest.original_url == original_url).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return {"short_url": f"http://localhost/{link.short_code}"}

@app.delete("/links/{short_code}")
def delete_link(short_code: str, db: Session = Depends(get_db)):
    link = db.query(LinkTest).filter(LinkTest.short_code == short_code).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    db.delete(link)
    db.commit()
    return {"message": "Link deleted successfully"}


if __name__ == "__main__":
    uvicorn.run("app:app", reload=True, host="0.0.0.0", log_level="info")
