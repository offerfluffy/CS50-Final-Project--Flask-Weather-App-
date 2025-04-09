import requests

from flask import session, redirect
from functools import wraps

api_key = "0c6ecd21053ce3886337191607f2fc70"


def get_weather(city):
    response = requests.get(
        f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&APPID={api_key}"
    )

    if response.status_code == 404:
        return {"error": "City not found. Please check the name and try again."}

    if response.status_code != 200:
        return {"error": "An error occurred. Please try again later."}

    data = response.json()

    weather_data = {
        "city": data.get("name"),
        "country": data.get("sys", {}).get("country"),
        "coordinates": {
            "longitude": data.get("coord", {}).get("lon"),
            "latitude": data.get("coord", {}).get("lat"),
        },
        "weather": {
            "main": data.get("weather", [{}])[0].get("main"),
            "description": data.get("weather", [{}])[0].get("description"),
            "icon": data.get("weather", [{}])[0].get("icon"),
        },
        "main": {
            "temperature": data.get("main", {}).get("temp"),
            "feels_like": data.get("main", {}).get("feels_like"),
            "temp_min": data.get("main", {}).get("temp_min"),
            "temp_max": data.get("main", {}).get("temp_max"),
            "pressure": data.get("main", {}).get("pressure"),
            "humidity": data.get("main", {}).get("humidity"),
        },
        "wind": {
            "speed": data.get("wind", {}).get("speed"),
            "degree": data.get("wind", {}).get("deg"),
        },
        "clouds": data.get("clouds", {}).get("all"),
        "visibility": data.get("visibility"),
        "sunrise": data.get("sys", {}).get("sunrise"),
        "sunset": data.get("sys", {}).get("sunset"),
        "timezone": data.get("timezone"),
        "timestamp": data.get("dt"),
    }

    return weather_data


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
