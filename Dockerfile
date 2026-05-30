# Usamos una base ligera de Python
FROM python:3.12-slim

# Instalar dependencias del sistema necesarias para Pandoc y XeLaTeX
RUN apt-get update && apt-get install -y \
    pandoc \
    texlive-xetex \
    texlive-fonts-recommended \
    texlive-plain-generic \
    && rm -rf /var/lib/apt/lists/*

# Crear carpeta de trabajo
WORKDIR /app

# Copiar los requerimientos e instalarlos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código de tu proyecto al contenedor
COPY . .

# Exponer el puerto donde corre la API (FastAPI usa el 8000 por defecto)
EXPOSE 8000

# Comando para arrancar el servidor
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
