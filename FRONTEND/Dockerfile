# Use the official image as a parent image
FROM python:3.8

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Streamlit runs on (Google Cloud Run uses port 8080)
EXPOSE 8080

# Set environment variables
ENV GOOGLE_APPLICATION_CREDENTIALS /app/keyfile.json

# Run Streamlit
ENTRYPOINT ["streamlit", "run", "meteo.py", "--server.port=8080", "--server.address=0.0.0.0"]
