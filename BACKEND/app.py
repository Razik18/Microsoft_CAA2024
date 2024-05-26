from flask import Flask, request, jsonify, send_file
import requests
import openai
from google.cloud import texttospeech, bigquery
import os
import json
from datetime import datetime
import pytz

app = Flask(__name__)

# Configuration
credential_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "keyfile.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credential_path
client = bigquery.Client(location="EU")

OPENWEATHER_API_KEY = ''
CITY_NAME = 'Lausanne'
OPENAI_API_KEY = ''


# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

# Initialize Google Cloud TTS client
tts_client = texttospeech.TextToSpeechClient()

def fetch_weather():
    url = f'http://api.openweathermap.org/data/2.5/weather?q={CITY_NAME}&appid={OPENWEATHER_API_KEY}&units=metric'
    response = requests.get(url)
    data = response.json()
    if response.status_code == 200:
        description = data['weather'][0]['description']
        temp = data['main']['temp']
        humidity = data['main']['humidity']
        return {
            "description": description,
            "temp": temp,
            "humidity": humidity,
            "weather_info": f"The current weather in {CITY_NAME} is {description} with a temperature of {temp} degrees Celsius and humidity of {humidity}%."
        }
    else:
        return None

def generate_weather_description(weather_info):
    prompt = f"Generate a sentence describing the following weather information: {weather_info}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    description = response.choices[0].message['content'].strip()
    return description


def text_to_speech(text):
    input_text = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )
    response = tts_client.synthesize_speech(
        input=input_text, voice=voice, audio_config=audio_config
    )
    audio_file = "weather_report.wav"
    with open(audio_file, "wb") as out:
        out.write(response.audio_content)
    return audio_file

def insert_into_bigquery(data):
    dataset_id = 'propro'  # Dataset ID
    table_id = 'weather-records'  # Table ID within the dataset
    table_ref = client.dataset(dataset_id).table(table_id)
    table = client.get_table(table_ref)

    now = datetime.now(pytz.timezone("Europe/Zurich"))
    date_str = now.date().isoformat()  # Format date
    time_str = now.strftime("%H:%M:%S")  # Format time

    rows_to_insert = [
        {
            "date": date_str,
            "time": time_str,
            "indoor_temp": data['indoor_temp'],
            "outdoor_temp": data['outdoor_temp'],
            "indoor_humidity": data['indoor_humidity'],
            "outdoor_humidity": data['outdoor_humidity'],
            "outdoor_weather": data['outdoor_weather'],
            "iaq": data['iaq']
        }
    ]

    errors = client.insert_rows_json(table, rows_to_insert)
    if errors == []:
        print("New rows have been added.")
    else:
        print("Encountered errors while inserting rows: {}".format(errors))
        raise Exception(errors)

@app.route('/postdata', methods=['POST'])
def postdata():
    try:
        data = request.get_json()
        print("Received data:", data)
        insert_into_bigquery(data)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/weather_report', methods=['GET'])
def weather_report():
    weather_data = fetch_weather()
    if not weather_data:
        return jsonify({"status": "error", "message": "Failed to fetch weather data"}), 500
    
    weather_description = generate_weather_description(weather_data['weather_info'])
    audio_file = text_to_speech(weather_description)
    
    return send_file(audio_file, mimetype='audio/wav')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
