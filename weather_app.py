import re
from configparser import ConfigParser
from tkinter import *
from tkinter import messagebox, ttk

import requests

from rate_limiter import check_and_increment, get_usage
from weather_utils import format_location, format_temperature, parse_weather_response

# Config

CONFIG_FILE = "config.ini"
config = ConfigParser()
config.read(CONFIG_FILE)

API_KEY       = config["pkn"]["api"]
DAILY_LIMIT   = config.getint("limits", "daily_limit",   fallback=50)
MONTHLY_LIMIT = config.getint("limits", "monthly_limit", fallback=500)

URL_BY_CITY = "https://api.openweathermap.org/data/2.5/weather?q={}&appid={}"
URL_BY_ZIP  = "https://api.openweathermap.org/data/2.5/weather?zip={}&appid={}"

US_STATES: dict[str, str] = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR",
    "california": "CA", "colorado": "CO", "connecticut": "CT",
    "delaware": "DE", "florida": "FL", "georgia": "GA", "hawaii": "HI",
    "idaho": "ID", "illinois": "IL", "indiana": "IN", "iowa": "IA",
    "kansas": "KS", "kentucky": "KY", "louisiana": "LA", "maine": "ME",
    "maryland": "MD", "massachusetts": "MA", "michigan": "MI",
    "minnesota": "MN", "mississippi": "MS", "missouri": "MO",
    "montana": "MT", "nebraska": "NE", "nevada": "NV",
    "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM",
    "new york": "NY", "north carolina": "NC", "north dakota": "ND",
    "ohio": "OH", "oklahoma": "OK", "oregon": "OR", "pennsylvania": "PA",
    "rhode island": "RI", "south carolina": "SC", "south dakota": "SD",
    "tennessee": "TN", "texas": "TX", "utah": "UT", "vermont": "VT",
    "virginia": "VA", "washington": "WA", "west virginia": "WV",
    "wisconsin": "WI", "wyoming": "WY",
}

# Query builder

def build_query(raw: str) -> tuple[str, str]:
    raw = raw.strip()

    if re.fullmatch(r"\d{5}(?:,\s*[A-Za-z]{2})?", raw):
        parts   = [p.strip() for p in raw.split(",")]
        country = parts[1].upper() if len(parts) == 2 else "US"
        zip_q   = f"{parts[0]},{country}"
        url     = URL_BY_ZIP.format(zip_q, API_KEY)
        return url, f"zip {zip_q}"

    parts = [p.strip() for p in raw.split(",")]
    city  = parts[0]

    if len(parts) == 1:
        url = URL_BY_CITY.format(city, API_KEY)
        return url, city

    region = parts[1]

    
    region_lower = region.lower()
    if region_lower in US_STATES:
        region = US_STATES[region_lower]

    if region.upper() in US_STATES.values():
        query = f"{city},{region.upper()},US"
    else:
        query = f"{city},{region.upper()}"

    url = URL_BY_CITY.format(query, API_KEY)
    return url, query


# API call

def get_weather(raw_input: str) -> dict | None:
    """
    Fetch weather for the given user input.
    Enforces rate limits before making the HTTP request.
    Returns a parsed weather dict, or None on failure.
    Raises RuntimeError with a user-friendly message when limits are hit.
    """
    allowed, message = check_and_increment(DAILY_LIMIT, MONTHLY_LIMIT)
    if not allowed:
        raise RuntimeError(message)

    url, _label = build_query(raw_input)
    response = requests.get(url, timeout=10)

    if response.status_code == 200:
        return parse_weather_response(response.json())
    elif response.status_code == 404:
        return None
    else:
        raise RuntimeError(
            f"API error {response.status_code}: {response.json().get('message', 'Unknown error')}"
        )


# UI

def search():
    raw = city_text.get().strip()
    if not raw:
        messagebox.showwarning("Input needed", "Please enter a city, state, or zip code.")
        return

    try:
        weather = get_weather(raw)
    except RuntimeError as e:
        messagebox.showerror("Limit reached", str(e))
        return
    except requests.exceptions.ConnectionError:
        messagebox.showerror("Network error", "Could not reach the weather service.\nCheck your internet connection.")
        return
    except requests.exceptions.Timeout:
        messagebox.showerror("Timeout", "The request timed out. Please try again.")
        return

    if weather is None:
        messagebox.showerror("Not found", f'Could not find weather for "{raw}".\nTry a different city name, state, or zip code.')
        return

    # Choose temperature unit from dropdown
    unit = unit_var.get()  # "F" or "C"
    temp  = weather["temp_f"]  if unit == "F" else weather["temp_c"]
    feels = weather["feels_f"] if unit == "F" else weather["feels_c"]

    location_lbl["text"]    = format_location(weather["city"], weather["country"])
    temperature_lbl["text"] = f"Temp: {format_temperature(temp, unit)}  (Feels like {format_temperature(feels, unit)})"
    description_lbl["text"] = weather["description"]
    humidity_lbl["text"]    = f"Humidity: {weather['humidity']}%"
    wind_lbl["text"]        = f"Wind: {weather['wind_mph']} mph"

    # Refresh status bar
    usage = get_usage()
    status_lbl["text"] = (
        f"API calls today: {usage['daily_count']}/{DAILY_LIMIT}  |  "
        f"This month: {usage['monthly_count']}/{MONTHLY_LIMIT}"
    )


# Build window
app = Tk()
app.title("Weather App")
app.geometry("360x340")
app.resizable(False, False)

# Search row
search_frame = Frame(app, pady=8)
search_frame.pack(fill=X, padx=10)

city_text  = StringVar()
city_entry = Entry(search_frame, textvariable=city_text, width=24, font=("Arial", 11))
city_entry.pack(side=LEFT, padx=(0, 6))
city_entry.insert(0, "City, State or Zip")
city_entry.bind("<FocusIn>",  lambda e: city_entry.delete(0, END) if city_entry.get() == "City, State or Zip" else None)
city_entry.bind("<Return>",   lambda e: search())

search_btn = Button(search_frame, text="Search", width=8, command=search)
search_btn.pack(side=LEFT)

# Unit toggle
unit_var = StringVar(value="F")
unit_frame = Frame(app)
unit_frame.pack()
Radiobutton(unit_frame, text="°F", variable=unit_var, value="F").pack(side=LEFT)
Radiobutton(unit_frame, text="°C", variable=unit_var, value="C").pack(side=LEFT)

# Result labels
result_frame = Frame(app, pady=6)
result_frame.pack(fill=X, padx=16)

location_lbl    = Label(result_frame, text="—",  font=("Arial", 14, "bold"))
temperature_lbl = Label(result_frame, text="",   font=("Arial", 12))
description_lbl = Label(result_frame, text="",   font=("Arial", 11, "italic"))
humidity_lbl    = Label(result_frame, text="",   font=("Arial", 10))
wind_lbl        = Label(result_frame, text="",   font=("Arial", 10))

for lbl in (location_lbl, temperature_lbl, description_lbl, humidity_lbl, wind_lbl):
    lbl.pack(anchor=W, pady=1)

# Status bar
usage        = get_usage()
status_frame = Frame(app, bd=1, relief=SUNKEN)
status_frame.pack(side=BOTTOM, fill=X)
status_lbl = Label(
    status_frame,
    text=(
        f"API calls today: {usage['daily_count']}/{DAILY_LIMIT}  |  "
        f"This month: {usage['monthly_count']}/{MONTHLY_LIMIT}"
    ),
    font=("Arial", 8),
    anchor=W,
    fg="gray40",
)
status_lbl.pack(fill=X, padx=4)

app.mainloop()
