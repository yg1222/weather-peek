from flask import Flask, render_template, redirect, request
import requests
import json
from datetime import datetime
import time
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)



api_key = os.getenv("api_key")
id = os.getenv("id")

UNITS = ["metric", "imperial"]

@app.route('/')
def index():
    return render_template("index.html", units=UNITS)


@app.route("/search", methods=['GET', 'POST'])
def search():
    # Location processing for geolocation
    city_query = str(request.form.get("city_query"))    
    location_data = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?appid={api_key}&limit=1&q={city_query}")
    unit = str(request.form.get("unit"))
    print("Got unit: " + unit)

    # Returns a list of dictionaries. Only one element in the list (0)
    location_data_dict = json.loads(location_data.content)
    location_data_dict = location_data_dict[0]

    # Location data variables
    lon = str(location_data_dict["lon"])
    lat = str(location_data_dict["lat"])
    print("User city Query resulting in geolocation:")
    print(city_query)
    print(lon)
    print(lat)

    # Weather: Used the 'forcast' call which adds the data to the 'list' list for every 3 hours for 5 days 
    weather_url = "http://api.openweathermap.org/data/2.5/forecast?" + "appid=" + api_key + "&id=" + id + "&lat=" + lat + "&lon=" + lon + "&units=" + unit
    print(weather_url)
    weather_data = requests.get(weather_url)   

    # Returns JSON file with a list as a value ti the key 'list' with 
    # multiple elements. I need the latest as it stores each API call in the list
    weather_data_json = json.loads(weather_data.content)

    # Weather data variables
    temperature = int(weather_data_json['list'][0]['main']['temp'])
    feels_like = weather_data_json['list'][0]['main']['feels_like']
    humidity = weather_data_json['list'][0]['main']['humidity']
    description = weather_data_json['list'][0]['weather'][0]['description']
    icon = weather_data_json['list'][0]['weather'][0]['icon']
    wind = weather_data_json['list'][0]['wind']['speed']      
    visibility = weather_data_json['list'][0]['visibility']
    city = weather_data_json['city']['name']
    country = weather_data_json['city']['country']
    # Timezone - Shift in seconds from UTC
    timezone = weather_data_json['city']['timezone']
    api_call_time = (weather_data_json['list'][0]['dt']) + timezone
    sunrise = (weather_data_json['city']['sunrise']) + timezone
    sunset = (weather_data_json['city']['sunset']) + timezone    
    
    # Converting variables to usable formats
    # Wind unit Default: meter/sec
    # Converting wind to km/h if metric and miles/hr if imperial
    # To KMpH
    icon_url = "https://openweathermap.org/img/wn/" + icon + "@2x.png"
    # Convert to metric 
    if (unit == UNITS[0]):
        wind = float(round((wind*3.6), 2))
        visibility = int(visibility/1000)
        wind_unit  = "Km/h"
        vis_unit = "Km"
        temp_unit = "C"
    # Convert to imperial
    elif (unit == UNITS[1]):
        wind = float(round((wind /0.44704), 2))
        visibility = int(visibility /1609.344)
        wind_unit = "Mph"
        vis_unit = "mi"
        temp_unit = "F"
    
    
    # Adjusting to the timezone of the current api call
    # Time stamp
    now = time.time()    
    now += timezone 
    print(now)    
    now = datetime.utcfromtimestamp(now).strftime('%A, %b %d - %H:%M')
    
    api_call_time = datetime.utcfromtimestamp(api_call_time).strftime('%Y-%m-%d %H:%M:%S')
    sunrise = datetime.utcfromtimestamp(sunrise).strftime('%H:%M')
    sunset = datetime.utcfromtimestamp(sunset).strftime('%H:%M')
    print("Sunrise: " + sunrise)
    print("Sunset: " + sunset)
    print("API call time: " + api_call_time)    
    print("Now time: " + now)

    print(icon)
    print(icon_url)

    # Icon or image handle
    # Idea: change background image depending on the weather description
    # TODO


    return render_template("search.html",city=city, temperature=temperature, feels_like=feels_like,  
    humidity=humidity, description=description, visibility=visibility, wind = wind, sunrise=sunrise, 
    sunset=sunset, now=now, units=UNITS, wind_unit=wind_unit, vis_unit=vis_unit, temp_unit=temp_unit, 
    country=country, icon_url=icon_url)


if __name__ == '__main__':
    app.run(debug=True)

    # FUTURE IMPLEMENTATIONS
    # Options for 5 day forcast
    