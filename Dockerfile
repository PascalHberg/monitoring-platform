# Offizielles, schlankes Python-Image als Basis
FROM python:3.13-slim

# Systemabhängigkeiten installieren (u.a. für Ping & Paramiko)
RUN apt-get update && apt-get install -y --no-install-recommends \
    iputils-ping \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Arbeitsverzeichnis im Container festlegen
WORKDIR /app

# Abhängigkeiten kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Anwendungs-Code kopieren
COPY . .

# Port für FastAPI/Uvicorn freigeben
EXPOSE 8000

# Startbefehl für den Uvicorn-Server im Container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]