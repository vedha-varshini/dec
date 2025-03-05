from flask import Flask, render_template, request
import requests
import os
import json
from datetime import datetime, timedelta

app = Flask(__name__)
CACHE_FILE = 'weatherstack_cache.json'
CACHE_DURATION = timedelta(minutes=30)

def get_cached_data(location):
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            cache = json.load(f)
        if location in cache and datetime.fromisoformat(cache[location]['timestamp']) + CACHE_DURATION > datetime.now():
            return cache[location]['data']
    return None

def save_to_cache(location, data):
    cache = {}
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            cache = json.load(f)
    cache[location] = {'timestamp': datetime.now().isoformat(), 'data': data}
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

@app.route('/', methods=['GET', 'POST'])
def weather():
    data = {}
    error = None
    location = request.form.get('location', 'New York').strip() if request.method == 'POST' else 'New York'
    
    cached_data = get_cached_data(location)
    if cached_data:
        data = cached_data
    else:
        try:
            url = "https://weatherstack.p.rapidapi.com/current"
            querystring = {"query": location}
            headers = {
                "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY"),
                "X-RapidAPI-Host": "weatherstack.p.rapidapi.com"
            }
            response = requests.get(url, headers=headers, params=querystring, timeout=10)
            response.raise_for_status()
            resp_json = response.json()
            if 'current' in resp_json:
                data = resp_json['current']
                data['location'] = resp_json.get('location', {})
                save_to_cache(location, data)
            else:
                error = resp_json.get('error', {}).get('info', 'Unknown API error')
        except requests.RequestException as e:
            error = f"Failed to fetch data: {str(e)}"
    
    return render_template('index_weatherstack.html', data=data, error=error)

if __name__ == '__main__':
    app.run(debug=False, port=5003, host='0.0.0.0')
