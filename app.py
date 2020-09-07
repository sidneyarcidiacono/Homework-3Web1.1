import jinja2
import matplotlib
import matplotlib.pyplot as plt
import os
from pprint import PrettyPrinter
import pytz
import requests

from datetime import datetime, timedelta, date
from dotenv import load_dotenv
from flask import Flask, render_template, request, send_file, abort, jsonify
from geopy.geocoders import Nominatim
from io import BytesIO
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from weather import Weather


################################################################################
## SETUP
################################################################################

app = Flask(__name__)

# Get the API key from the '.env' file
load_dotenv()
API_KEY = os.getenv('API_KEY')

#Make a PrettyPrinter object
pp = PrettyPrinter(indent=4)

#Get today's date
today = date.today()

#make textual day, month, year
date_today = today.strftime('%B %d, %Y')

# Settings for image endpoint
# Written with help from http://dataviztalk.blogspot.com/2016/01/serving-matplotlib-plot-that-follows.html
matplotlib.use('agg')
plt.style.use('ggplot')

my_loader = jinja2.ChoiceLoader([
    app.jinja_loader,
    jinja2.FileSystemLoader('data'),
])
app.jinja_loader = my_loader


weather_app = Weather()

################################################################################
## ROUTES
################################################################################

@app.route('/')
def home():
    """Displays the homepage with forms for current or historical data."""
    context = {
        'min_date': (datetime.now() - timedelta(days=5)),
        'max_date': datetime.now()
    }
    return render_template('home.html', **context)



@app.errorhandler(500)
def error_page(e):
    print(e)
    return render_template('404.html'), 500



@app.route('/results')
def results():
    """Displays results for current weather conditions."""
    city = request.args.get('city')
    state = request.args.get('state')
    units = request.args.get('units')
    url = weather_app.url
    lat, lon = weather_app.get_lat_lon(city)

    params = {
        'appid': API_KEY,
        'lat': lat,
        'lon': lon,
        'units': units,
        'dt': weather_app.date_in_seconds,
        'exclude': 'hourly'
    }

#TODO: See if you can make below variables a reusable function in weather.py
    result_json = requests.get(url, params=params).json()
    current_result = result_json['current']

    pp.pprint(result_json)

    # weather = result_json.get('weather')

    context = {
        'date': weather_app.date_today,
        'city': city,
        'state': state,
        'description': current_result['weather'][0]['description'],
        'icon': current_result['weather'][0]['icon'],
        'temp': current_result['temp'],
        'humidity': current_result['humidity'],
        'wind_speed': current_result['wind_speed'],
        'sunrise': datetime.fromtimestamp(current_result['sunrise']),
        'sunset': datetime.fromtimestamp(current_result['sunrise']),
        'units_letter': weather_app.get_letter_for_units(units)
    }

    return render_template('results.html', **context)


#Functions to return values for below routes

def get_min_temp(results):
    """Returns the minimum temp for the given hourly weather objects."""
    temps = []
    for i in results:
        temp = i['temp']
        temps.append(temp)
    min_temp = min(temps)
    return min_temp


def get_max_temp(results):
    """Returns the maximum temp for the given hourly weather objects."""
    temps = []
    for i in results:
        temp = i['temp']
        temps.append(temp)
    max_temp = max(temps)
    return max_temp



@app.route('/historical_results')
def historical_results():
    """Displays historical weather forecast for a given day."""

    city = request.args.get('city')
    date = request.args.get('date')
    units = request.args.get('units')
    date_obj = datetime.strptime(date, '%m-%d-%Y')
    date_in_seconds = date_obj.strftime('%s')

    latitude, longitude = weather_app.get_lat_lon(city)
    url = weather_app.url

    params = {
        'appid': API_KEY,
        'lat': latitude,
        'lon': longitude,
        'units': units,
        'dt': date_in_seconds
    }

    result_json = requests.get(url, params=params).json()

    pp.pprint(result_json)

    result_current = result_json['current']
    result_hourly = result_json['hourly']

    context = {
        'city': city,
        'date': date_obj,
        'lat': latitude,
        'lon': longitude,
        'units': units,
        'units_letter': weather_app.get_letter_for_units(units), # should be 'C', 'F', or 'K'
        'description': result_current['weather'][0]['description'],
        'temp': result_current['temp'],
        'min_temp': get_min_temp(result_hourly),
        'max_temp': get_max_temp(result_hourly),
        'icon': result_current['weather'][0]['icon']
    }

    return render_template('historical_results.html', **context)


@app.route('/forecast_results')
def forecast_results():
    """Displays future weather forecast for a given day."""

    city = request.args.get('city')
    date = request.args.get('date')
    units = request.args.get('units')
    date_obj = datetime.strptime(date, '%m-%d-%Y')
    date_in_seconds = date_obj.strftime('%s')

    latitude, longitude = weather_app.get_lat_lon(city)

    url = weather_app.url
    params = {
        'appid': API_KEY,
        'lat': latitude,
        'lon': longitude,
        'units': units,
        'dt': date_in_seconds
    }

    result_json = requests.get(url, params=params).json()

    pp.pprint(result_json)

    result_hourly = result_json['hourly']
    result_current = result_json['current']

    context = {
        'city': city,
        'date': date_obj,
        'lat': latitude,
        'lon': longitude,
        'units': units,
        'units_letter': weather_app.get_letter_for_units(units), # should be 'C', 'F', or 'K'
        'description': result_current['weather'][0]['description'],
        'temp': result_current['temp'],
        'min_temp': get_min_temp(result_hourly),
        'max_temp': get_max_temp(result_hourly),
        'icon': result_current['weather'][0]['icon']
    }

    return render_template('forecast_results.html', **context)


################################################################################
## IMAGES
################################################################################

def create_image_file(xAxisData, yAxisData, xLabel, yLabel):
    """
    Creates and returns a line graph with the given data.
    Written with help from http://dataviztalk.blogspot.com/2016/01/serving-matplotlib-plot-that-follows.html
    """
    fig, _ = plt.subplots()
    plt.plot(xAxisData, yAxisData)
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    canvas = FigureCanvas(fig)
    img = BytesIO()
    fig.savefig(img)
    img.seek(0)
    return send_file(img, mimetype='image/png')

@app.route('/graph/<lat>/<lon>/<units>/<date>')
def graph(lat, lon, units, date):
    """
    Returns a line graph with data for the given location & date.
    @param lat The latitude.
    @param lon The longitude.
    @param units The units (imperial, metric, or kelvin)
    @param date The date, in the format %Y-%m-%d.
    """
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    date_in_seconds = date_obj.strftime('%s')


    url = 'http://api.openweathermap.org/data/2.5/onecall/timemachine'
    params = {
        'appid': API_KEY,
        'lat': lat,
        'lon': lon,
        'units': units,
        'dt': date_in_seconds
    }
    result_json = requests.get(url, params=params).json()

    hour_results = result_json['hourly']

    hours = range(24)
    temps = [r['temp'] for r in hour_results]
    image = create_image_file(
        hours,
        temps,
        'Hour',
        f'Temperature ({get_letter_for_units(units)})'
    )
    return image



if __name__ == '__main__':
    app.run()
