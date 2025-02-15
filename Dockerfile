# Use an official Python image
FROM python:3.9

# Set working directory
WORKDIR /app

# Copy dependency list and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Expose API port
EXPOSE 8000

# Run the FastAPI application with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
