FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY DinnerSchool/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /app/DinnerSchool

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate --no-input && python manage.py crear_grupos && python manage.py collectstatic --no-input && daphne -b 0.0.0.0 -p 8000 mysite.asgi:application"]
