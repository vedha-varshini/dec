from flask import Flask, render_template, request
import requests
import os
import json
from datetime import datetime, timedelta

app = Flask(__name__)
CACHE_FILE = 'ipgeo_cache.json'
CACHE_DURATION = timedelta(minutes=30)

def get_cached_data(ip):
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            cache = json.load(f)
        if ip in cache and datetime.fromisoformat(cache[ip]['timestamp']) + CACHE_DURATION > datetime.now():
            return cache[ip]['data']
    return None

def save_to_cache(ip, data):
    cache = {}
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            cache = json.load(f)
    cache[ip] = {'timestamp': datetime.now().isoformat(), 'data': data}
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

@app.route('/', methods=['GET', 'POST'])
def ip_geolocation():
    data = {}
    error = None
    ip = request.form.get('ip', '').strip() if request.method == 'POST' else ''
    
    cached_data = get_cached_data(ip)
    if cached_data:
        data = cached_data
    else:
        try:
            url = "https://ip-geolocation-ipwhois-io.p.rapidapi.com/json/"
            querystring = {"ip": ip} if ip else {}
            headers = {
                "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY"),
                "X-RapidAPI-Host": "ip-geolocation-ipwhois-io.p.rapidapi.com"
            }
            response = requests.get(url, headers=headers, params=querystring, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get('success', True):  # Check API success flag
                save_to_cache(ip, data)
            else:
                error = data.get('message', 'Unknown API error')
        except requests.RequestException as e:
            error = f"Failed to fetch data: {str(e)}"
    
    return render_template('index_ipgeo.html', data=data, error=error)

if __name__ == '__main__':
    app.run(debug=False, port=5001, host='0.0.0.0')
