import requests
import datetime


# Ваш API ключ OpenWeatherMap
API_KEY = "YOUR_API_KEY"


def get_weather_day(city_name):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}q={city_name}&appid={API_KEY}"
    
    response = requests.get(complete_url)
    
    if response.status_code == 200:
        data = response.json()
        main = data['main']
        wind = data['wind']
        weather_description = data['weather'][0]['description']
        icon_code = data['weather'][0]['icon']  # Код иконки погоды
        day = datetime.datetime.fromtimestamp(data['dt']).strftime('%A')
        
        temperature_celsius = main['temp'] - 273.15
        
        pressure_mm_hg = main['pressure'] * 0.75006375541921
        
        return {
            'day': day,
            'city': city_name,
            'temperature': round(temperature_celsius),
            'pressure': round(pressure_mm_hg),
            'humidity': main['humidity'],
            'wind_speed': wind['speed'],
            'description': weather_description,
            'icon': f"http://openweathermap.org/img/wn/{icon_code}@2x.png"  # URL иконки
        }
    else:
        return None

def get_geo_data(city_name):
    geocoding_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&appid={API_KEY}"
    geo_response = requests.get(geocoding_url)
    
    if geo_response.status_code == 200:
        geo_data = geo_response.json()
        if len(geo_data) == 0:
            return None

        lat = geo_data[0]['lat']
        lon = geo_data[0]['lon']
        
    if get_weather_day(city_name) == None:
        return None
    
    return lat, lon
