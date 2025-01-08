
# Use official Python image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
EXPOSE 8020

# Command to run the app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8020"]