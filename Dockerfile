# Imagen base oficial de Python
FROM python:3.11-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar requirements y luego instalar las dependencias de Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Instalar las herramientas necesarias del sistema (nmap, dnsutils, whois)
RUN apt-get update && \
    apt-get install -y nmap dnsutils whois

# Copiar el resto del proyecto al contenedor
COPY . .

# Variables de entorno para optimizar la ejecución de Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Exponer el puerto 8000 para acceder a Django
EXPOSE 8000

# Comando para ejecutar el servidor de desarrollo de Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
