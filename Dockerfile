# Base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the script
COPY weather_analyzer.py .

# Create a directory for output
RUN mkdir -p /app/output

# Set entrypoint
ENTRYPOINT ["python", "weather_analyzer.py"]