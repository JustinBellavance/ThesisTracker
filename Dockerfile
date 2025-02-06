# Use the official Python image from the Docker Hub
FROM ghcr.io/astral-sh/uv:python3.12-alpine

# Create and set the working directory inside the container
WORKDIR /app

# Copy the rest of your Django project files into the container
ADD . /app/

# Expose port 8000 for the Django app
EXPOSE 8000

# Set the default command to run the Django development server
CMD ["uv", "run", "manage.py", "runserver", "0.0.0.0:8000"]