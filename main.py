import tkinter as tk
from tkinter import ttk
import requests
from PIL import Image, ImageTk
from geopy.geocoders import Nominatim
from io import BytesIO

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

    for widget in forecast_frame.winfo_children():
        widget.destroy()

    for i, period in enumerate(periods[:4]):
        frame = tk.Frame(forecast_frame, bg="#f0f0f0", padx=10, pady=10, relief="ridge", bd=2)
        frame.grid(row=0, column=i, padx=5, pady=5)

        # Fetch icon
        icon_url = period["icon"]
        try:
            img_data = requests.get(icon_url).content
            img = Image.open(BytesIO(img_data))
            img = img.resize((64, 64))
            photo = ImageTk.PhotoImage(img)
        except:
            photo = None

        if photo:
            label_icon = tk.Label(frame, image=photo, bg="#f0f0f0")
            label_icon.image = photo  # keep reference
            label_icon.pack()

        label_title = tk.Label(frame, text=period["name"], font=("Helvetica", 12, "bold"), bg="#f0f0f0")
        label_title.pack()

        label_temp = tk.Label(frame, text=f"{period['temperature']}°{period['temperatureUnit']}", font=("Helvetica", 12), bg="#f0f0f0")
        label_temp.pack()

        label_forecast = tk.Label(frame, text=period["shortForecast"], wraplength=150, justify="center", bg="#f0f0f0")
        label_forecast.pack()


# GUI
root = tk.Tk()
root.title("Project Weather App")
root.config(bg="#d9f0ff")

title = tk.Label(root, text = "Weather Forecast", font = ("Helvetica", 16, "bold"), bg = "#d9f0ff")
title.pack(pady = 10)

tk.Label(root, text = "Enter location (ZIP or City, State):").pack(pady = 5)
entry = tk.Entry(root, width = 40)
entry.pack(pady = 5)

tk.Button(root, text = "Get Weather", command = getWeather).pack(pady = 10)

result_label = tk.Label(root, text = "", wraplength = 300, justify = "left")
result_label.pack(pady = 10)

forecast_frame = tk.Frame(root, bg = "#d9f0ff")
forecast_frame.pack(pady = 10)

root.mainloop()