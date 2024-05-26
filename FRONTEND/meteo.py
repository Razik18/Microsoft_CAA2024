import streamlit as st
import requests
from datetime import datetime, timedelta
import base64
import os
import plotly.graph_objects as go
import openai
from google.cloud import bigquery
from google.oauth2 import service_account

# OpenAI API details
openai.api_key = ''

# GCP credentials
credential_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "keyfile.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credential_path
client = bigquery.Client(location="EU")

# Function to encode GIF as base64
def get_base64_image(file_path):
    with open(file_path, "rb") as file_:
        contents = file_.read()
    data_url = base64.b64encode(contents).decode("utf-8")
    return data_url

# Paths to the GIFs for different weather conditions
gif_paths = {
    'Clear': ('sun.gif', 60),
    'Clouds': ('cloud.gif', 80),
    'Rain': ('rain-cloud.gif', 50),
}

# Function to get the latest data from BigQuery
def get_latest_data(dataset_id, table_id):
    query = f"""
        SELECT * FROM `{dataset_id}.{table_id}`
        ORDER BY date DESC, time DESC
        LIMIT 1
    """
    query_job = client.query(query)
    results = query_job.result()
    df = results.to_dataframe()
    
    if not df.empty:
        latest_data = df.iloc[0]  # Get the latest row of data
        formatted_data = {
            'Date': latest_data['date'],
            'Time': latest_data['time'],
            'Indoor Temperature': latest_data['indoor_temp'],
            'Outdoor Temperature': latest_data['outdoor_temp'],
            'Indoor Humidity': latest_data['indoor_humidity'],
            'Outdoor Humidity': latest_data['outdoor_humidity'],
            'Outdoor Weather': latest_data['outdoor_weather'],
            'IAQ': latest_data['iaq'],
        }
        return formatted_data
    else:
        return None

# Function to get BigQuery data
def get_bigquery_data(dataset_id, table_id):
    query = f"""SELECT * FROM `{dataset_id}.{table_id}`
    ORDER BY date DESC, time DESC"""
    query_job = client.query(query)
    results = query_job.result()
    return results.to_dataframe()

# Function to get weather GIF based on weather condition
def get_weather_gif(condition):
    for key in gif_paths:
        if key in condition:
            return gif_paths[key]
    return gif_paths['Clear']

# OpenWeather API details
api_key = 'e183192c5f47def67e159019ff5ecf91'
base_url = 'http://api.openweathermap.org/data/2.5/'

# Get weather data from OpenWeather API
def get_weather_data(city):
    url = f"{base_url}weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    return data

# Get forecast data from OpenWeather API
def get_forecast_data(city):
    url = f"{base_url}forecast?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    return data

# Get city suggestions from Mapbox API
def get_city_suggestions(query, access_token):
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{query}.json"
    params = {
        "access_token": access_token,
        "autocomplete": True,
        "types": "place"
    }
    response = requests.get(url, params=params)
    data = response.json()
    suggestions = [feature['place_name'] for feature in data['features']]
    return suggestions

# Function to generate weather description using OpenAI
def generate_weather_description(weather_data):
    prompt = f"Generate a detailed weather description for the following data:\n\n{weather_data}\n\nDescription:"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that provides detailed weather descriptions."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=100
    )
    description = response['choices'][0]['message']['content'].strip()
    return description

# Streamlit App
st.title('Weekly Weather Forecast')

# Background color
st.markdown(
    """
    <style>
    .stApp {
        background-color: #FFFDF4;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Add a search bar to input city name
city_input = st.text_input('Enter city name')

# Your Mapbox API access token
mapbox_token = 'pk.eyJ1IjoibmFiejAxIiwiYSI6ImNsd2lnNWRqejA0emoya2xhdHk0cHlwMTMifQ.TyX5Q_g9L0gAiFDV4dt9GQ'  # Replace with your actual Mapbox access token

# Get city suggestions based on user input
if city_input:
    suggestions = get_city_suggestions(city_input, mapbox_token)
    if suggestions:
        city = st.selectbox('Select a city', suggestions)
    else:
        city = None
else:
    city = 'Lausanne'

# Initialize favorites list in session state
if 'favorites' not in st.session_state:
    st.session_state.favorites = []

# Add a button to add the city to favorites
if city:
    if st.button('Add to Favorites'):
        st.session_state.favorites.append(city)

# Display favorites in the sidebar
st.sidebar.title("Favorites")
selected_city = city
for favorite in st.session_state.favorites:
    col1, col2 = st.sidebar.columns([3, 1])
    with col1:
        if col1.button(favorite):
            selected_city = favorite
    with col2:
        if col2.button('X', key=f'remove_' + favorite):
            st.session_state.favorites.remove(favorite)
            st.experimental_rerun()

if selected_city:
    # Extract city name from the suggestion
    city_name = selected_city.split(',')[0]

    # Get today's weather data
    today_weather_data = get_weather_data(city_name)
    if 'weather' in today_weather_data:
        today_condition = today_weather_data['weather'][0]['main']
        today_description = generate_weather_description(today_weather_data)
        today_temperature = today_weather_data['main']['temp']
        today_date = datetime.now().strftime('%Y-%m-%d')
        today_wind = today_weather_data['wind']['speed']
        today_wind_deg = today_weather_data['wind']['deg']
        today_pressure = today_weather_data['main']['pressure']
        today_humidity = today_weather_data['main']['humidity']
        today_coords = today_weather_data['coord']
    else:
        st.error("Error: Unexpected response format for today's weather data")
        st.json(today_weather_data)  # Print the full response for debugging
        st.stop()

    # Display today's weather
    st.markdown(f"**Today's Weather in {city_name}**")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f'<span style="color:blue">{today_date}</span>', unsafe_allow_html=True)
        today_gif, today_gif_width = get_weather_gif(today_condition)
        today_gif_base64 = get_base64_image(today_gif)
        st.markdown(
            f'<img src="data:image/gif;base64,{today_gif_base64}" width="{today_gif_width}" alt="{today_condition}">',
            unsafe_allow_html=True,
        )
        st.markdown(f'<span style="color:orange">{today_temperature}°C, {today_condition}</span>', unsafe_allow_html=True)
        st.markdown(f'Coordinates: {today_coords["lat"]}, {today_coords["lon"]}')
    with col2:
        st.markdown(f'Coordinates: {today_coords["lat"]}, {today_coords["lon"]}')
        st.markdown(f'Wind: {today_wind} m/s SW')
        st.markdown(f'Pressure: {today_pressure} hPa')
        st.markdown(f'Humidity: {today_humidity} %')
    st.markdown(f'**Description**: {today_description}')

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button(f"**Get more details thanks to your M5 stack!**", key='custom-button'):
            dataset_id = 'propro'  # Replace with your dataset ID
            table_id = 'weather-records'  # Replace with your table ID
            details_data = get_latest_data(dataset_id, table_id)
            if details_data:
                st.markdown("### Latest Data from M5stack")
                st.markdown(f"**Indoor Temperature**: {details_data['Indoor Temperature']} °C")
                st.markdown(f"**Indoor Humidity**: {details_data['Indoor Humidity']} %")
                st.markdown(f"**Indoor air quality**: {details_data['IAQ']}")
            else:
                st.error("No data available.")
    with col2: 
            if st.button(f"**Get historical data from M5 stack!**"):
                dataset_id = 'propro'  # Replace with your dataset ID
                table_id = 'weather-records'  # Replace with your table ID
                details_data = get_bigquery_data(dataset_id, table_id)
                st.write(details_data)

    # Display hourly forecast for today
    forecast_data = get_forecast_data(city_name)
    hourly_weather = {}
    for entry in forecast_data['list']:
        date = entry['dt_txt'].split()[0]
        time = entry['dt_txt'].split()[1]
        if date == today_date:
            if date not in hourly_weather:
                hourly_weather[date] = []
            hourly_weather[date].append(entry)

    st.markdown("### Hourly Forecast for Today")
    hourly_cols = st.columns(len(hourly_weather[today_date]))
    for i, entry in enumerate(hourly_weather[today_date]):
        time = entry['dt_txt'].split()[1]
        temp = entry['main']['temp']
        condition = entry['weather'][0]['main']
        gif, gif_width = get_weather_gif(condition)
        gif_base64 = get_base64_image(gif)
        with hourly_cols[i]:
            st.markdown(f"**{time}**")
            st.markdown(f'<img src="data:image/gif;base64,{gif_base64}" width="{gif_width}" alt="{condition}">', unsafe_allow_html=True)
            st.markdown(f'<span style="color:orange">{temp}°C, {condition}</span>', unsafe_allow_html=True)

    # Display days of the week with temperatures and GIFs in a horizontal line
    weekly_weather = {}
    for entry in forecast_data['list']:
        date = entry['dt_txt'].split()[0]
        time = entry['dt_txt'].split()[1]
        if date not in weekly_weather:
            weekly_weather[date] = {'morning': None, 'evening': None}
        if time == '03:00:00':
            weekly_weather[date]['morning'] = entry
        elif time == '18:00:00':
            weekly_weather[date]['evening'] = entry

    st.title('Days of the Week')
    cols = st.columns(len(weekly_weather))
    for i, (day, data) in enumerate(weekly_weather.items()):
        morning_data = data['morning']
        evening_data = data['evening']
        morning_condition = morning_data['weather'][0]['main'] if morning_data else 'N/A'
        evening_condition = evening_data['weather'][0]['main'] if evening_data else 'N/A'
        morning_temp = morning_data['main']['temp'] if morning_data else 'N/A'
        evening_temp = evening_data['main']['temp'] if evening_data else 'N/A'
        morning_gif, morning_gif_width = get_weather_gif(morning_condition)
        morning_gif_base64 = get_base64_image(morning_gif)
        evening_gif, evening_gif_width = get_weather_gif(evening_condition)
        evening_gif_base64 = get_base64_image(evening_gif)
        with cols[i]:
            date = datetime.strptime(day, '%Y-%m-%d')
            day_of_week = date.strftime('%A')
            st.write(f"**{day_of_week}**")
            st.markdown(f'<span style="color:blue">{date.strftime("%Y-%m-%d")}</span>', unsafe_allow_html=True)
            st.markdown(
                f'<img src="data:image/gif;base64,{morning_gif_base64}" width="{morning_gif_width}" alt="{morning_condition}"> ',
                unsafe_allow_html=True,
            )
            st.markdown(f'<span style="color:orange">{morning_temp} / {evening_temp}°C</span>', unsafe_allow_html=True)

    # Add an option for auto-refresh
    st.sidebar.title("Options")
    auto_refresh = st.sidebar.checkbox('Auto Refresh', value=False)
    refresh_interval = st.sidebar.number_input('Refresh Interval (minutes)', min_value=1, value=5)
    if auto_refresh:
        import time
        st.experimental_rerun()
        time.sleep(refresh_interval * 60)

    st.markdown("Compare your favorite cities: Simply add cities to your favorites to display the plot.")
    # Plot the forecast data
    fig = go.Figure()
    for favorite in st.session_state.favorites:
        forecast_data = get_forecast_data(favorite.split(',')[0])
        dates = []
        temps_evening = []
        for entry in forecast_data['list']:
            date = entry['dt_txt'].split()[0]
            time = entry['dt_txt'].split()[1]
            if time == '21:00:00':
                dates.append(date)
                temps_evening.append(entry['main']['temp'])
        fig.add_trace(go.Scatter(x=dates, y=temps_evening, mode='lines+markers', name=f'Evening Temp: {favorite.split(",")[0]}'))
    fig.update_layout(title='Evening Temperature Forecast Comparison', xaxis_title='Date', yaxis_title='Temperature (°C)')
    st.plotly_chart(fig)
