FROM python:3.11-slim

WORKDIR /workspace/fastapi

COPY fastapi/requirements.txt /workspace/fastapi/requirements.txt
RUN pip install --no-cache-dir -r /workspace/fastapi/requirements.txt

COPY fastapi/app /workspace/fastapi/app

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
