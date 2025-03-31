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