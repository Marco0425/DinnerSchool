# 🐍 Imagen base con Python 3.11.6
FROM python:3.11.6-slim

# 🛠️ Establece directorio de trabajo
WORKDIR /app

# 🔒 Evita archivos pyc y activa UTF-8
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8

# 📦 Instala dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 📥 Copia archivos de requerimientos (ajusta la ruta si es necesario)
COPY DinnerSchool/requirements.txt .

# 📦 Instala dependencias de Python
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# 📁 Copia el resto del proyecto
COPY . .

# 🐍 Mensaje opcional para debug
RUN echo "Archivos copiados y dependencias instaladas correctamente"

# ⚙️ Recoge archivos estáticos (Django)
RUN python DinnerSchool/manage.py collectstatic --noinput

# 🚀 Comando de arranque con Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "DinnerSchool.mysite.wsgi:application"]