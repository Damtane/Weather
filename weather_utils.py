import math


def kelvin_to_celsius(k: float) -> float:
    return round(k - 273.15, 1)


def kelvin_to_fahrenheit(k: float) -> int:
    return math.ceil((k * 1.8) - 459.67)


def celsius_to_fahrenheit(c: float) -> int:
    return math.ceil((c * 9 / 5) + 32)


def format_location(city: str, country: str) -> str:
    return f"{city}, {country}"


def format_temperature(value: float | int, unit: str) -> str:
    symbol = "°F" if unit == "F" else "°C"
    return f"{value}{symbol}"


def parse_weather_response(json_data: dict) -> dict:
    temp_k = json_data["main"]["temp"]
    feels_k = json_data["main"]["feels_like"]
    humidity = json_data["main"]["humidity"]
    wind_speed = json_data.get("wind", {}).get("speed", 0)  # m/s from OWM
    wind_mph = round(wind_speed * 2.237, 1)                 # convert to mph

    return {
        "city":        json_data["name"],
        "country":     json_data["sys"]["country"],
        "temp_c":      kelvin_to_celsius(temp_k),
        "temp_f":      kelvin_to_fahrenheit(temp_k),
        "feels_c":     kelvin_to_celsius(feels_k),
        "feels_f":     kelvin_to_fahrenheit(feels_k),
        "humidity":    humidity,
        "wind_mph":    wind_mph,
        "description": json_data["weather"][0]["description"].title(),
        "main":        json_data["weather"][0]["main"],
    }