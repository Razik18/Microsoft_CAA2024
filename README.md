# Weather Forecasting System

## Project Members
- Abderazzak Saib
- Nabil Ajiach

## Overview
This project is a comprehensive weather forecasting system that integrates various technologies to provide real-time weather information, indoor and outdoor environmental data, and detailed weather reports. The system includes three main components: a backend server, an M5Stack-based IoT device, and a frontend web application built with Streamlit.

## Backend (Flask Server)
The backend server is built using Flask and provides endpoints for receiving data from the M5Stack device, fetching weather data from the OpenWeather API, generating weather descriptions using OpenAI's GPT-3.5-turbo, and converting text to speech using Google Cloud's Text-to-Speech API.

### Key Functionalities:
1. **Weather Data Fetching**:
   - Fetches real-time weather data for a specified city using the OpenWeather API.
   - Generates a descriptive weather report using OpenAI's GPT-3.5-turbo.
   - Converts the weather report to an audio file using Google Cloud's Text-to-Speech API.

2. **Data Insertion into BigQuery**:
   - Receives environmental data from the M5Stack device.
   - Inserts the data into a Google BigQuery table for storage and further analysis.

3. **Endpoints**:
   - `/postdata`: Receives environmental data from the M5Stack device and stores it in BigQuery.
   - `/weather_report`: Fetches real-time weather data, generates a description, and returns an audio file of the weather report.

## M5Stack Device
The M5Stack device is an IoT device that collects indoor environmental data (temperature, humidity, IAQ) and sends it to the backend server. It also fetches weather data from the backend and displays it on its screen.

### Key Components:
1. **ENV III Unit**:
   - Measures indoor temperature and humidity.
   - Provides accurate and real-time environmental data for indoor conditions.

2. **TVOC/CO2 Unit**:
   - Measures indoor air quality by detecting Total Volatile Organic Compounds (TVOC) and CO2 levels.
   - Helps in monitoring indoor air quality and ensuring a healthy indoor environment.

### Functionality:
- **Data Collection**: The M5Stack device continuously collects data from the ENV III and TVOC/CO2 units.
- **Data Transmission**: The collected data is sent to the backend server at regular intervals.
- **Weather Display**: Fetches weather data from the backend server and displays it on the screen.
- **Vocal Weather Reports**: Plays audio weather reports fetched from the backend server.

## Frontend (Streamlit App)
The frontend application is built using Streamlit and provides a user-friendly interface for users to interact with the system. It allows users to:
- View real-time weather data and forecasts.
- Get detailed weather descriptions.
- Visualize indoor and outdoor environmental data collected by the M5Stack device.
- Compare weather data for multiple cities.

### Link to Frontend
Access the frontend application here: [Frontend Application](https://ccapro-2dnhgbbuua-ew.a.run.app/)

**Note**: Make sure your browser is not in dark mode.

## Deployment Instructions
To deploy this system, follow these steps:

### Set Up Google Cloud Credentials
1. Place your Google Cloud service account key file (`keyfile.json`) in the root directory of the project.
2. Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to point to your key file:

### Update API Keys
1. Open `app.py` and update the placeholders with your actual API keys for OpenAI, OpenWeather, and Google Cloud.

### Install Dependencies
1. Create a virtual environment and install the required packages.

### Run the Flask Server
1. Start the Flask server to handle backend operations.

### Run the Streamlit App
1. Launch the Streamlit application to access the frontend interface.

## Conclusion
This weather forecasting system leverages IoT, machine learning, and cloud technologies to provide comprehensive weather information and environmental data. By following the deployment instructions and ensuring the necessary API keys are in place, you can set up and run this system to monitor and analyze weather data effectively.

### Watch Our Demo Video
Watch the demo video here: [YouTube Video](www.youtube.com)
