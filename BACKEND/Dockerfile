# Use a specific version of Python in a slim variant
FROM python:3.9-slim-buster

# Set the working directory inside the container
WORKDIR /app

# Install the Python dependencies specified in requirements.txt
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application's source code into the working directory
COPY . /app

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Set an environment variable to specify the Python file to run as the main application
ENV FLASK_APP=app.py

# Environment variable for Google Cloud credentials, set to be configured at runtime
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/keyfile.json

# Command to run the Flask application using the Flask CLI
CMD ["flask", "run", "--host", "0.0.0.0", "--port", "8080"]
