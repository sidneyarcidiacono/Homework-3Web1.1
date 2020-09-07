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
        self._date_in_seconds = self.date_obj.strftime('%s')
        self._city = ''
        self._state = ''
        self._units = ''
        self._result_hourly = ''
        self._result_current = ''

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

    def set_date(self, date):
        """Set date to user input rather than default (today)."""
        if date == self.date_string:
            return
        else:
            try:
                self.date_obj = datetime.strptime(date, '%m-%d-%Y')
                self._date_in_seconds = self.date_obj.strftime('%s')
            except ValueError:
                print('Incorrect date format')

    def set_city(self, city):
        """Set city to user input rather than default."""
        self._city = city

    def set_state(self, state):
        """Set state to user input rather than default."""
        self._state = state

    def set_units(self, units):
        """Set units to user input rather than default."""
        self._units = units

    def set_current_hourly_result(self, result):
        """Set hourly result."""
        self._result_hourly = result['hourly']
        self._result_current = result['current']

    def get_min_temp(self, results):
        """Return the minimum temp for the given hourly weather objects."""
        temps = []
        for i in results:
            temp = i['temp']
            temps.append(temp)
        min_temp = min(temps)
        return min_temp


    def get_max_temp(self, results):
        """Return the maximum temp for the given hourly weather objects."""
        temps = []
        for i in results:
            temp = i['temp']
            temps.append(temp)
        max_temp = max(temps)
        return max_temp
