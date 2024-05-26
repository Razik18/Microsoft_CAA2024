from m5stack import *
from m5stack_ui import *
from uiflow import *
import ntptime
import unit
import wifiCfg
import urequests
import json
import _thread
import time
from libs.image_plus import *

# Initialize the screen
screen = M5Screen()
screen.clean_screen()
screen.set_screen_bg_color(0xffffff)
env3_2 = unit.get(unit.ENV3, unit.PORTA)

# Function to connect to Wi-Fi using stored SSID and password
def connect_to_wifi():
    wifiCfg.doConnect(ssid, wifi_password)

# Initialize sensors
env3 = unit.get(unit.ENV3, unit.PORTA)
tvoc_sensor = unit.get(unit.TVOC, unit.PORTC)

# UI Labels for weather and sensor data
weather_label = M5Label('Weather:', x=20, y=10, color=0x000, font=FONT_MONT_26, parent=None)
label_outdoor_temp = M5Label('Outdoor Temp: -- °C', x=20, y=50, color=0x000, font=FONT_MONT_18, parent=None)
label_outdoor_humi = M5Label('Outdoor Humi: -- %', x=20, y=90, color=0x000, font=FONT_MONT_18, parent=None)
label_indoor_temp = M5Label('Indoor Temp: -- °C', x=20, y=130, color=0x000, font=FONT_MONT_18, parent=None)
label_indoor_humi = M5Label('Indoor Humi: -- %', x=20, y=170, color=0x000, font=FONT_MONT_18, parent=None)
label_iaq = M5Label('IAQ: --', x=20, y=210, color=0x000, font=FONT_MONT_18, parent=None)

# Forecast Labels
forecast_label = M5Label('Forecast: Lausanne', x=20, y=10, color=0x000, font=FONT_MONT_26, parent=None)
forecast_label.set_hidden(True)  # Hide forecast label by default
forecast_dates = [M5Label('', x=20 + i*100, y=60, color=0x000, font=FONT_MONT_22, parent=None) for i in range(3)]
forecast_temps = [M5Label('', x=20 + i*100, y=90, color=0x000, font=FONT_MONT_22, parent=None) for i in range(3)]

# Icon URLs for forecast images
icon_url1 = ''
icon_url2 = ''
icon_url3 = ''
forecast_images = []  # To store M5ImagePlus instances

# Initial display labels
label0 = M5Label('Weather M5', x=80, y=19, color=0x000, font=FONT_MONT_26, parent=None)
label2 = M5Label('', x=116, y=129, color=0x000, font=FONT_MONT_14, parent=None)
label3 = M5Label('', x=90, y=89, color=0x000, font=FONT_MONT_38, parent=None)
label4 = M5Label('Home', x=243, y=208, color=0x000, font=FONT_MONT_18, parent=None)
label5 = M5Label('Weather', x=121, y=208, color=0x000, font=FONT_MONT_18, parent=None)
label6 = M5Label('Forecast', x=17, y=208, color=0x000, font=FONT_MONT_18, parent=None)
line1 = M5Line(x1=107, y1=196, x2=107, y2=284, color=0x000, width=6, parent=None)
line0 = M5Line(x1=220, y1=194, x2=220, y2=281, color=0x000, width=6, parent=None)
line2 = M5Line(x1=0, y1=60, x2=350, y2=60, color=0x000000, width=5, parent=None)
line3 = M5Line(x1=0, y1=50, x2=320, y2=50, color=0x000, width=5, parent=None)
line4 = M5Line(x1=107, y1=50, x2=107, y2=315, color=0x000, width=5, parent=None)
line5 = M5Line(x1=210, y1=50, x2=210, y2=315, color=0x000, width=5, parent=None)

# Touch Button
touch_button0 = M5Btn(text='Vocal Weather', x=10, y=156, w=300, h=40, bg_c=0xe3e3e3, text_c=0x665454, font=FONT_MONT_14, parent=None)
touch_button1 = M5Btn(text='WIFI', x=8, y=16, w=50, h=30, bg_c=0xFFFFFF, text_c=0x000000, font=FONT_MONT_14, parent=None)

# Wi-Fi SSID and Password
ssid = ""
wifi_password = ""

# Labels for SSID and Password
label_ssid = M5Label('SSID:', x=20, y=100, color=0x000, font=FONT_MONT_26, parent=None)
label_ssid_value = M5Label('', x=150, y=100, color=0x000, font=FONT_MONT_26, parent=None)
label_password = M5Label('Password:', x=20, y=150, color=0x000, font=FONT_MONT_26, parent=None)
label_password_value = M5Label('', x=150, y=150, color=0x000, font=FONT_MONT_26, parent=None)
label_status = M5Label('', x=20, y=200, color=0x000000, font=FONT_MONT_26)

# Button to save SSID and Wi-Fi Password
button_save = M5Btn(text='Save', x=100, y=250, w=120, h=40, bg_c=0x007BFF, text_c=0xFFFFFF, font=FONT_MONT_26, parent=None)
button_save.set_hidden(True)

# Hide Wi-Fi labels initially
label_ssid.set_hidden(True)
label_ssid_value.set_hidden(True)
label_password.set_hidden(True)
label_password_value.set_hidden(True)
label_status.set_hidden(True)
line3.set_hidden(True)
line4.set_hidden(True)
line5.set_hidden(True)

# Wi-Fi connection status
wifi_connected = False

# Warning label for no Wi-Fi connection
label_warning = M5Label('Connect to Wi-Fi first', x=20, y=100, color=0xFF0000, font=FONT_MONT_26, parent=None)
label_warning.set_hidden(True)

# Hide weather details initially
weather_label.set_hidden(True)
label_outdoor_temp.set_hidden(True)
label_outdoor_humi.set_hidden(True)
label_indoor_temp.set_hidden(True)
label_indoor_humi.set_hidden(True)
label_iaq.set_hidden(True)

# Flags to control the threads and display
stop_stats_thread = False
stats_thread_started = False
stop_time_thread = False
time_thread_started = False

outdoor_temp = None
outdoor_humi = None
weather_description = None

# Function to display outdoor temperature and humidity
def TempLabelDisplay(temp, humi):
    label_outdoor_temp.set_text('Outdoor Temp: {:.2f} °C'.format(temp))
    label_outdoor_humi.set_text('Outdoor Humi: {:.2f} %'.format(humi))

# Function to update the weather description label
def update_weather_display(weather_description):
    weather_label.set_text('Weather: {}'.format(weather_description))

# Function to fetch the current weather data
def fetch_weather():
    global outdoor_temp, outdoor_humi, weather_description
    if not wifiCfg.wlan_sta.isconnected():
        connect_to_wifi()
    if wifiCfg.wlan_sta.isconnected():
        url = 'http://api.openweathermap.org/data/2.5/weather?q=Lausanne&appid=e183192c5f47def67e159019ff5ecf91'
        response = urequests.get(url)
        if response.status_code == 200:
            data = json.loads(response.text)
            outdoor_temp = data['main']['temp'] - 273.15  # Convert Kelvin to Celsius
            outdoor_humi = data['main']['humidity']
            weather_description = data['weather'][0]['main']
            update_weather_display(weather_description)
            TempLabelDisplay(outdoor_temp, outdoor_humi)
            response.close()
        else:
            weather_label.set_text('Failed to fetch weather')
            response.close()

# Function to fetch the weather forecast
def fetch_forecast():
    global icon_url1, icon_url2, icon_url3, forecast_images
    if not wifiCfg.wlan_sta.isconnected():
        connect_to_wifi()
    if wifiCfg.wlan_sta.isconnected():
        url = 'http://api.openweathermap.org/data/2.5/forecast?q=Lausanne&cnt=32&appid=e183192c5f47def67e159019ff5ecf91'
        response = urequests.get(url)
        if response.status_code == 200:
            data = json.loads(response.text)
            forecast = []
            for i in range(1, 4):  # Skip today's forecast and get the next 3 days
                day_forecast = data['list'][i * 8]  # Get forecast at 24-hour intervals (8 * 3-hour intervals)
                temp = int(day_forecast['main']['temp'] - 273.15)  # Convert Kelvin to Celsius and cast to int
                date = day_forecast['dt_txt'].split(' ')[0][5:]  # Get the date and remove the year
                icon = day_forecast['weather'][0]['icon']  # Get the weather icon code
                icon_url = 'http://openweathermap.org/img/wn/' + icon + '@2x.png'  # Correct string formatting
                forecast.append((date, temp, icon_url))
            icon_url1 = forecast[0][2]
            icon_url2 = forecast[1][2]
            icon_url3 = forecast[2][2]
            for i in range(3):
                forecast_dates[i].set_text(forecast[i][0])
                forecast_dates[i].set_hidden(False)
                forecast_temps[i].set_text('{} °C'.format(forecast[i][1]))
                forecast_temps[i].set_hidden(False)
            forecast_images = [
                M5ImagePlus(220, 129, url=icon_url1),
                M5ImagePlus(120, 129, url=icon_url2),
                M5ImagePlus(20, 129, url=icon_url3)
            ]
            response.close()
            return forecast
        else:
            forecast_label.set_text('Failed to fetch forecast')
            response.close()
    return None

# Function to read sensor data (temperature, humidity, IAQ)
def read_sensors():
    temperature = env3.temperature
    humidity = env3.humidity
    iaq = tvoc_sensor.TVOC
    label_indoor_temp.set_text('Indoor Temp: {:.2f} °C'.format(temperature))
    label_indoor_humi.set_text('Indoor Humi: {:.2f} %'.format(humidity))
    label_iaq.set_text('IAQ: {}'.format(iaq))
    
    # Change background color if IAQ is over 150
    if iaq > 150:
        rgb.setColorAll(0xff0000)
        rgb.setBrightness(10)
    else:
        rgb.setBrightness(0)  # Red
    
    return temperature, humidity, iaq

# Function to send sensor and weather data to a server
def send_data(indoor_temp, indoor_humi, iaq, outdoor_temp, outdoor_humi, weather_description):
    url = 'https://cca-2dnhgbbuua-ew.a.run.app/postdata'  
    headers = {'Content-Type': 'application/json'}
    data = {
        "indoor_temp": indoor_temp,
        "outdoor_temp": outdoor_temp,
        "indoor_humidity": indoor_humi,
        "outdoor_humidity": outdoor_humi,
        "outdoor_weather": weather_description,
        "iaq": iaq  # Include IAQ data
    }
    try:
        print("Sending data:", data)
        response = urequests.post(url, data=json.dumps(data), headers=headers)
        print("Data sent. Response:", response.text)
    except Exception as e:
        print("Failed to send data:", str(e))

# Function to hide all labels and UI elements
def hide_labels():
    weather_label.set_hidden(True)
    label_outdoor_temp.set_hidden(True)
    label_outdoor_humi.set_hidden(True)
    label_indoor_temp.set_hidden(True)
    label_indoor_humi.set_hidden(True)
    label_iaq.set_hidden(True)
    forecast_label.set_hidden(True)
    for i in range(3):
        forecast_dates[i].set_hidden(True)
        forecast_temps[i].set_hidden(True)
    for img in forecast_images:
        img.hide()  # Use img.hide() to hide images
    label0.set_hidden(True)
    label2.set_hidden(True)
    label3.set_hidden(True)
    label4.set_hidden(True)
    label5.set_hidden(True)
    label6.set_hidden(True)
    line0.set_hidden(True)
    line1.set_hidden(True)
    line2.set_hidden(True)
    line3.set_hidden(True)
    line4.set_hidden(True)
    line5.set_hidden(True)
    touch_button0.set_hidden(True)
    touch_button1.set_hidden(True)  # Hide the touch button
    label_ssid.set_hidden(True)
    label_ssid_value.set_hidden(True)
    label_password.set_hidden(True)
    label_password_value.set_hidden(True)
    button_save.set_hidden(True)
    label_status.set_hidden(True)
    label_warning.set_hidden(True)

# Function to show the main menu labels and UI elements
def show_time_labels():
    label0.set_hidden(False)
    label2.set_hidden(False)
    label3.set_hidden(False)
    label4.set_hidden(False)
    label5.set_hidden(False)
    label6.set_hidden(False)
    line0.set_hidden(False)
    line1.set_hidden(False)
    line2.set_hidden(False)
    touch_button0.set_hidden(False)
    touch_button1.set_hidden(False)  # Show the touch button

# Function to update the time display
def update_time(ntp):
    while not stop_time_thread:
        label2.set_text(str(ntp.formatDate('-')))
        label3.set_text(str(ntp.formatTime(':')))
        wait(1)

# Function called when Button A is pressed
def buttonA_wasPressed():
    global stop_time_thread, wifi_connected
    if not wifi_connected:
        screen.set_screen_bg_color(0xffffff)
        hide_labels()
        label_warning.set_hidden(False)
    else:
        stop_time_thread = True  # Stop time thread
        screen.set_screen_bg_color(0xffffff)
        hide_labels()
        line3.set_hidden(False)
        line4.set_hidden(False)
        line5.set_hidden(False)
        fetch_forecast()  # Fetch and display the forecast
        forecast_label.set_hidden(False)  # Show forecast label
        for img in forecast_images:
            img.set_hidden(False)  # Use set_hidden(False) to show images
        print("Button A was pressed. Screen color changed to white, labels hidden, and forecast displayed.")

# Function called when Button B is pressed
def buttonB_wasPressed():
    global stop_stats_thread, stats_thread_started, stop_time_thread, wifi_connected
    if not wifi_connected:
        screen.set_screen_bg_color(0xffffff)
        hide_labels()
        label_warning.set_hidden(False)
    else:
        stop_time_thread = True  # Stop time thread
        screen.set_screen_bg_color(0xffffff)
        hide_labels()
        weather_label.set_hidden(False)
        label_outdoor_temp.set_hidden(False)
        label_outdoor_humi.set_hidden(False)
        label_indoor_temp.set_hidden(False)
        label_indoor_humi.set_hidden(False)
        label_iaq.set_hidden(False)
        read_sensors()  # Immediately read and display sensor data
        fetch_weather()  # Fetch and display outdoor weather stats
        if not stats_thread_started:
            stats_thread_started = True
            stop_stats_thread = False
            _thread.start_new_thread(stats_thread, ())
        print("Button B was pressed. Screen color changed to white, weather details shown.")

# Function called when Button C is pressed
def buttonC_wasPressed():
    global stop_stats_thread, stats_thread_started, stop_time_thread, time_thread_started
    stop_stats_thread = True
    stats_thread_started = False
    stop_time_thread = True
    screen.set_screen_bg_color(0xffffff)
    hide_labels()
    show_time_labels()
    stop_time_thread = False  # Restart time thread
    if not time_thread_started:
        time_thread_started = True
        _thread.start_new_thread(update_time, (ntptime.client(host='de.pool.ntp.org', timezone=2),))
    print("Button C was pressed. Returned to the main menu with time display.")

# Function to fetch and play a weather report audio file
def fetch_and_play_wav():
    if not wifiCfg.wlan_sta.isconnected():
        connect_to_wifi()
    if wifiCfg.wlan_sta.isconnected():
        url = 'https://cca-2dnhgbbuua-ew.a.run.app/weather_report'  # Replace with your server's IP and port
        response = urequests.get(url)
        if response.status_code == 200:
            with open('/flash/weather_report.wav', 'wb') as f:
                f.write(response.content)
            response.close()
            speaker.playWAV('/flash/weather_report.wav', volume=84)
        else:
            response.close()
            print("Failed to fetch the WAV file")

# Function called when Touch Button 0 is pressed
def touch_button0_wasPressed():
    fetch_and_play_wav()

# Function called when Touch Button 1 (Wi-Fi button) is pressed
def touch_button1_wasPressed():
    global ssid, wifi_password, wifi_connected
    screen.set_screen_bg_color(0xffffff)
    hide_labels()
    label_ssid.set_hidden(False)
    label_ssid_value.set_hidden(False)
    label_password.set_hidden(False)
    label_password_value.set_hidden(False)
    button_save.set_hidden(False)
    label_status.set_hidden(False)
    link = 'https://flow.m5stack.com/remote?id=963236141124026368'
    lcd.qrcode(link, 75, 32, 176)
    wait(10)
    lcd.clear()  # Clear the screen to hide the QR code
    wifi_connected = True  # Assume connection is successful after entering SSID and password

# Callback function for SSID input
def input_1_callback(input_value):
    global ssid
    ssid = str(input_value)
    label_ssid_value.set_text(ssid)

# Callback function for Wi-Fi password input
def input_2_callback(input_value):
    global wifi_password
    wifi_password = str(input_value)
    label_password_value.set_text(wifi_password)

# Function called when the Save button is pressed
def button_save_callback():
    global ssid, wifi_password
    print("SSID:", ssid)
    print("Password:", wifi_password)
    label_status.set_text('SSID and Password Saved')
    with open('/flash/wifi_credentials.txt', 'w') as f:
        f.write("SSID: " + ssid + "\nPassword: " + wifi_password)

button_save.pressed(button_save_callback)

touch_button0.pressed(touch_button0_wasPressed)
touch_button1.pressed(touch_button1_wasPressed)

# Thread function to read sensors and send data periodically
def stats_thread():
    global stop_stats_thread, outdoor_temp, outdoor_humi, weather_description
    while not stop_stats_thread:
        indoor_temp, indoor_humi, iaq = read_sensors()
        send_data(indoor_temp, indoor_humi, iaq, outdoor_temp, outdoor_humi, weather_description)
        wait(5)  # Update every 5 seconds

# Register button A, B, and C press events
btnA.wasPressed(buttonA_wasPressed)
btnB.wasPressed(buttonB_wasPressed)
btnC.wasPressed(buttonC_wasPressed)

# Main function to fetch weather data and update time
def main():
    ntp = ntptime.client(host='de.pool.ntp.org', timezone=2)
    fetch_weather()  # Initial fetch of weather data
    while True:
        if not stop_time_thread:
            update_time(ntp)
        wait(1)  # Update time every second

# Start the main function in a new thread
_thread.start_new_thread(main, ())
