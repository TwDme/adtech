FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the application code into the container
COPY app.py db.py  db_config.py models.py schemas.py .
COPY data/ ./data/

EXPOSE 5000


CMD ["fastapi", "run", "app.py", "--port", "5000"]

