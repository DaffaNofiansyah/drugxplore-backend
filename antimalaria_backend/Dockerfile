# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install required system dependencies (including wget and curl)
RUN apt-get update && apt-get install -y wget curl && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy project files
COPY . /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt


ENV PYTHONUNBUFFERED 1
ENV DEBUG=False

# Expose the port the app will run on
EXPOSE 8080

# Run the application
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "-k", "gevent", "antimalaria_backend.wsgi:application"]
# CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "--keep-alive", "10", "antimalaria_backend.wsgi:application"]
CMD ["gunicorn", "--workers", "1", "--timeout", "120", "--keep-alive", "10", "antimalaria_backend.wsgi:application"]
