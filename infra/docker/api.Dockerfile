FROM python:3.11-slim

WORKDIR /workspace/apps/api

COPY apps/api /workspace/apps/api

RUN pip install --no-cache-dir -e .

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
