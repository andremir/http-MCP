FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the server code
COPY server_sse.py .

# Expose the port
EXPOSE 8000

# Run the server
CMD ["python", "server_sse.py"]