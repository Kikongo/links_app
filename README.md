# API-сервис сокращения ссылок

Cервис, который позволяет пользователям сокращать длинные ссылки, получать их аналитику и управлять ими.

### How to run it on your own machine

1. Add .env file and write DB_USER=user
DB_PASS=password
DB_HOST=host
DB_PORT=port
DB_NAME=db_name
SMTP_PASSWORD = password
SMTP_USER = user

2. Build docker

   ```
   $ docker build . -t fastapi_app:latest

   $ docker run -d -p 7329:8000 fastapi_app

   $ docker compose build

   $ docker compose up
   ```

### Структура БД:

Таблица user

   ```
class User(Base):
    __tablename__ = "user"

    id = Column(UUID, primary_key=True, index=True)
    email = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    registered_at = Column(TIMESTAMP, default=datetime.utcnow)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=True, nullable=False)

   ```

Таблица links

   ```
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

   ```

### Запуск тестов

   ```
$ pytest -v

$ locust -f tests/test_load.py --host=http://localhost:8000

   ```
