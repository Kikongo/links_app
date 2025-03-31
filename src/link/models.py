from sqlalchemy import Table, Column, Integer, DateTime, MetaData, String
metadata = MetaData()
from datetime import datetime

link = Table(
    "link",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("original_url", String, nullable=False),
    Column("short_code", String, unique=True, index=True, nullable=False),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("expires_at", DateTime, nullable=True),
    Column("visit_count", Integer, default=0),
    Column("last_visited", DateTime, nullable=True)
)

