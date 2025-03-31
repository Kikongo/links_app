from datetime import datetime, timedelta
from pydantic import BaseModel, HttpUrl

class ShortenRequest(BaseModel):
    original_url: HttpUrl
    custom_alias: str | None = None
    expires_at: datetime | None = datetime.now() + timedelta(days=1, hours=3)