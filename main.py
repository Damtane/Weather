import tkinter as tk
import requests
from geopy.geocoders import Nominatim

def getWeather():
    location = entry.get()
    geolocator = Nominatim(user_agent = "weather_app")
    loc = geolocator.geocode(location)

    if not loc:
        result_label.config(text = "Location not found.")
        return
    
    lat, lon = loc.latitude, loc.longitude

    # Gridpoint from National Weather Service
    pointURL = f"https://api.weather.gov/points/{lat},{lon}"
    response = requests.get(pointURL)
    if response.status_code != 200:
        result_label.config(text = "Error fetching gridpoint data.")
        return
    
    data = response.json()
    forecast_url = data["properties"]["forecast"]

    # Get forecast
    forecast_response = requests.get(forecast_url)
    if forecast_response.status_code != 200:
        result_label.config(text = "Error fetching forecast.")
        return
    
    forecast_data = forecast_response.json()
    periods = forecast_data["properties"]["periods"]

    # 1st forecast period
    first = periods[0]
    forecast_text = f"{first['name']}: {first['detailedForecast']}"
    result_label.config(text = forecast_text)


# GUI
root = tk.Tk()
root.title("Project Weather App")

tk.Label(root, text = "Enter location (ZIP or City, State):").pack(pady = 5)
entry = tk.Entry(root, width = 40)
entry.pack(pady = 5)

tk.Button(root, text = "Get Weather", command = getWeather).pack(pady = 10)

result_label = tk.Label(root, text = "", wraplength = 300, justify = "left")
result_label.pack(pady = 10)

root.mainloop()