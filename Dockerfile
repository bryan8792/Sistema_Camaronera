FROM python:3.10-slim

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema (si necesitas Pillow, psycopg2, etc.)
RUN apt-get update \
    && apt-get install -y build-essential libpq-dev python3-dev \
    && apt-get clean

# Copiar los archivos
COPY . /app/

# Instalar las dependencias de Python
RUN pip install --upgrade pip
RUN pip install -r requirements/base.txt  # o requirements.txt si solo tienes uno

# Exponer el puerto de Django
EXPOSE 8000

# Comando por defecto
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
