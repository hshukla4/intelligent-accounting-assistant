# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose a port if you're building a web API
# EXPOSE 8080

# Define environment variables (or load from /run/secrets for production)
ENV GCP_PROJECT_ID=your-gcp-project-id
ENV GCP_REGION=us-central1
# ... other settings from config/settings.py
# In Cloud Run, it's better to pass these as service environment variables

# Command to run the application (e.g., if you have a Flask/FastAPI app in src/api/app.py)
# CMD ["python", "src/api/app.py"]
# Or, if this container is for a batch job
# CMD ["python", "src/main.py"]
