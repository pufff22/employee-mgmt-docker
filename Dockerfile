# Small official Python image
FROM python:3.12-slim

# All app files live in /app inside the container
WORKDIR /app

# Install libraries first (Docker caches this step, so rebuilds are fast)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# The database file lives in /data so it can be kept in a Docker volume
ENV DATABASE_PATH=/data/employees.db
RUN mkdir -p /data

# The app listens on port 5000
EXPOSE 5000

# gunicorn is the production web server (Flask's built-in one is for development)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
