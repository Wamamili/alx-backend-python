# Use official Python image
FROM python:3.10

# Prevent Python from writing pyc files & buffering
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory inside container
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project files
COPY . /app/

# Expose the default Django port
EXPOSE 8000

# Run Django app with the -p flag for port binding
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000", "-p"]
