FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the contents of the src directory into the working directory
COPY ./src .

# Run the application from main.py
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

