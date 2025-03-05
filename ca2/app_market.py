from flask import Flask, render_template
import requests
import os
import json
from datetime import datetime, timedelta

app = Flask(__name__)
CACHE_FILE = 'marketstack_cache.json'
CACHE_DURATION = timedelta(hours=1)

def get_cached_data():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            cache = json.load(f)
        if datetime.fromisoformat(cache['timestamp']) + CACHE_DURATION > datetime.now():
            return cache['data']
    return None

def save_to_cache(data):
    cache = {'timestamp': datetime.now().isoformat(), 'data': data}
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

@app.route('/')
def stock_data():
    data = get_cached_data()
    error = None
    
    if data is None:
        try:
            url = "https://marketstack.p.rapidapi.com/v1/eod"
            querystring = {"symbols": "AAPL", "limit": "5"}
            headers = {
                "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY"),
                "X-RapidAPI-Host": "marketstack.p.rapidapi.com"
            }
            response = requests.get(url, headers=headers, params=querystring, timeout=10)
            response.raise_for_status()
            data = response.json().get('data', [])
            save_to_cache(data)
        except requests.RequestException as e:
            error = f"Failed to fetch data: {str(e)}"
            data = []
    
    return render_template('index_marketstack.html', data=data, error=error)

if __name__ == '__main__':
    app.run(debug=False, port=5002, host='0.0.0.0')
