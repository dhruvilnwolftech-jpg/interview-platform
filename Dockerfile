FROM python:3.10-slim

WORKDIR /app

COPY requirements_minimal.txt .

RUN pip install --no-cache-dir -r requirements_minimal.txt

COPY backend/ ./backend/
COPY tests/ ./tests/

EXPOSE 5000

CMD ["python", "backend/server.py"]
