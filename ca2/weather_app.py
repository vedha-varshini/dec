# app.py
from flask import Flask, render_template, request
import requests
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta
import base64
from io import BytesIO

app = Flask(__name__)

# API configuration
API_KEY = "207847adb8msh94744171f8832d6p1cba76jsn720da22eb090"
BASE_URL = "https://open-weather13.p.rapidapi.com/city/"
HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "open-weather13.p.rapidapi.com"
}


def get_weather(city):
    url = f"{BASE_URL}{city}/EN"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        if 'main' not in data:
            return {"error": "Invalid response format from API"}
        return data
    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP Error {e.response.status_code}: {e.response.reason}"}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}



@app.route('/', methods=['GET', 'POST'])
def index():
    weather_data = None
    plot_url = None
    error = None

    if request.method == 'POST':
        city = request.form.get('city')
        if city:  # This checks if city is not None and not an empty string
            weather_data = get_weather(city)

            if "error" not in weather_data:
                try:
                    current_temp = weather_data['main']['temp']
                    current_temp = (current_temp - 32) * 5 / 9  # Convert F to C
                except KeyError:
                    error = "Invalid weather data format received from API"
            else:
                error = weather_data["error"]
        else:
            error = "Please enter a city name"

    return render_template('index.html',
                           weather_data=weather_data,
                           plot_url=plot_url,
                           error=error)


if __name__ == '__main__':
    app.run(debug=True)
