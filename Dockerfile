FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . /app/

# Expose port for the app
EXPOSE 8000

# Run Django app
# Test
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
