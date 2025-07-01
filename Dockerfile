# Use official Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y build-essential libpq-dev

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port
EXPOSE 8000

# Start app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
