from configparser import ConfigParser
import requests
import math
import counterapi
from tkinter import *
from tkinter import messagebox


# The GeeksforGeeks page used snake case (temp_kelvin)
# but I prefer camel case for my variables.

configFile = "config.ini"
config = ConfigParser()
config.read(configFile)
api_key = config['pkn']['api']
url = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid={}'

def getweather(city):
    result = requests.get(url.format(city, api_key))
    counterapi.updateCounter()
    
    if result:
        json = result.json()
        city = json['name']
        country = json['sys']['country']
        temp_kelvin = json['main']['temp']
        temp_celsius = temp_kelvin-273.15
        tempFarhenheit = math.ceil((temp_kelvin * 1.8) - 459.67) 
        weather1 = json['weather'][0]['main']
        final = [city, country, temp_kelvin, 
                 temp_celsius, tempFarhenheit, weather1]
        return final
    else:
        print("NO Content Found")


# explicit function to
# search city
def search():
    city = city_text.get()
    weather = getweather(city)
    if weather:
        location_lbl['text'] = '{}, {}'.format(weather[0], weather[1])
        temperature_label['text'] = str(weather[4])+" Degree Fahrenheit"
        weather_l['text'] = weather[5]
    else:
        messagebox.showerror('Error', "Cannot find {}".format(city))


# Driver Code
# create object
app = Tk()
# add title
app.title("Weather Search")
# adjust window size
app.geometry("300x300")

# add labels, buttons and text
city_text = StringVar()
city_entry = Entry(app, textvariable=city_text)
city_entry.pack()
Search_btn = Button(app, text="Search a city", 
                    width=12, command=search)
Search_btn.pack()
location_lbl = Label(app, text="Location", font={'bold', 20})
location_lbl.pack()
temperature_label = Label(app, text="")
temperature_label.pack()
weather_l = Label(app, text="")
weather_l.pack()
app.mainloop()
