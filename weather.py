"""Import important things."""
from datetime import date, datetime
from flask import Flask, render_template, request, send_file, abort, jsonify
from geopy.geocoders import Nominatim


class Weather:
    """Define Weather class to reduce reused code."""

    def __init__(self):
        """Initialize Weather properties."""
        self.url = 'http://api.openweathermap.org/data/2.5/onecall'
        self.date = date.today()
        self.date_string = self.date.strftime('%m-%d-%Y')
        self.date_obj = datetime.strptime(self.date_string, '%m-%d-%Y')
        self.date_in_seconds = self.date_obj.strftime('%s')


    def get_letter_for_units(self, units):
        """Return a shorthand letter for the given units."""
        return 'F' if units == 'imperial' else 'C' if units == 'metric' else 'K'

    def get_lat_lon(self, city_name):
        """Get latitude & longitude based off of city."""
        geolocator = Nominatim(user_agent='Weather Application')
        location = geolocator.geocode(city_name)
        if location is not None:
            return location.latitude, location.longitude
        return 0, 0
