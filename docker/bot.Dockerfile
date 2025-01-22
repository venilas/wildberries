FROM python:3.12-slim

WORKDIR /app
COPY bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot/ /app/
COPY models.py /app/
CMD ["python", "run.py"]