FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the application code into the container
COPY app.py db.py  .
COPY data/ ./data/

EXPOSE 5000
# ENV FLASK_APP=app.py


CMD ["python3", "app.py"]

