FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY 1agent ./1agent
COPY 1backend ./1backend
COPY 1database ./1database
COPY 1frontend ./1frontend
COPY 1memory ./1memory
COPY 1tools ./1tools

EXPOSE 8501

CMD ["streamlit", "run", "1frontend/app.py", "--server.address=0.0.0.0", "--server.port=8501"]