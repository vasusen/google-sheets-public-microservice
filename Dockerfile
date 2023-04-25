# Use the official Python base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and templates
COPY app.py .
COPY templates/ templates/

# Expose the application port
EXPOSE 8080

# Start the application
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
