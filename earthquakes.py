import math
import json
import numpy as np
from pathlib import Path


def ensure_numeric(value):
    """This function will evaluate the value:
    if value is an int or float, it will be returned
    if value is a string it will try to convert to float:
        if it fails will raise a TypeError
        if it succeeds it will return the float value
    """
    if isinstance(value, (int, float)):
        return value
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"{value} is not a numeric value")


def calc_distance(lat1, lon1, lat2, lon2):
    """This function will calculate the distance between two coordinates
    the coordinates are given through latitude and longitude (degrees).
    The distance is calculated used the haversine formula
    The calculated distance will be in kilometers."""

    # Ensure the coordinates are numeric

    lat1 = ensure_numeric(lat1)
    lon1 = ensure_numeric(lon1)
    lat2 = ensure_numeric(lat2)
    lon2 = ensure_numeric(lon2)

    _earth_radius = 6_371_000

    lat1_radian = lat1 * math.pi / 180
    lat2_radian = lat2 * math.pi / 180

    lat_variation = (lat2 - lat1) * math.pi / 180
    long_variation = (lon2 - lon1) * math.pi / 180

    a = math.pow(math.sin(lat_variation / 2), 2) + math.cos(lat1_radian) * math.cos(lat2_radian) * math.pow(
        math.sin(long_variation / 2), 2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance_meters = _earth_radius * c
    distance_kms = distance_meters / 1000

    return distance_kms


def filter_invalid_earthquakes(earthquakes, magnitude_list, felt_list, significance_list, lat_list, long_list):
    """This function receives a dictionary of earthquakes
    and discards the invalid ones. Valid earthquakes are those
    that meet the following criteria:

    1. The 'geometry' type is 'Point'.
    2. The 'type' is 'Feature'.
    3. The coordinates are in a tuple format (validated by the coordinate_is_tuple function).
    4. The 'properties' dictionary contains the keys: 'mag', 'time', 'felt', 'sig', 'type', and 'magType'.

    Valid earthquakes will be added in a list of Quake objects"""

    valid_earthquakes = []

    for earthquake in earthquakes['features']:
        if 'coordinates' in earthquake['geometry']:
            if earthquake['geometry']['type'] == "Point" and earthquake['type'] == "Feature":
                if coordinate_is_tuple(earthquake):
                    if ('mag' in earthquake['properties'] and
                            'time' in earthquake['properties'] and
                            'felt' in earthquake['properties'] and
                            'sig' in earthquake['properties'] and
                            'type' in earthquake['properties'] and
                            'magType' in earthquake['properties'] and
                            isinstance(earthquake['properties']['felt'], (int, float))):
                        valid_earthquakes.append(earthquake)
    quakes_list = []
    for earthquake in valid_earthquakes:
        try:
            felt_list.append(int(earthquake['properties']['felt']))

            quakes_list.append(
                Quake(float(earthquake['properties']['mag']), int(earthquake['properties']['time']),
                      int(earthquake['properties']['felt']), int(earthquake['properties']['sig']),
                      earthquake['properties']['type'], earthquake['geometry']['coordinates']))

            magnitude_list.append(float(earthquake['properties']['mag']))
            significance_list.append(int(earthquake['properties']['sig']))
            lat_list.append(float(earthquake['geometry']['coordinates'][0]))
            long_list.append(float(earthquake['geometry']['coordinates'][1]))

        except ValueError as e:
            continue
    return quakes_list


def coordinate_is_tuple(earthquake):
    """This function will check if the coordinates are a valid tuple"""
    coordinates = earthquake['geometry']['coordinates']

    if isinstance(coordinates, (tuple, list)) and len(coordinates) == 3:
        for coordinate in coordinates:
            if not isinstance(coordinate, (int, float)):
                return False
        return True
    else:
        return False


class QuakeData:
    def __init__(self, earthquakes):
        magnitude_list = []
        felt_list = []
        significance_list = []
        lat_list = []
        long_list = []

        self.location_filter = None
        self.property_filter = None

        # this function will filter the earthquakes
        # create a list of Quake objects and update the list passed in the arguments
        quakes = filter_invalid_earthquakes(earthquakes, magnitude_list, felt_list,
                                            significance_list, lat_list, long_list)

        # create the dtype for the np array
        dtype_arr = np.dtype([
            ('quake', object),
            ('magnitude', np.float64),
            ('felt', np.int32),
            ('significance', np.int32),
            ('lat', np.float64),
            ('long', np.float64)
        ])

        # create an empty array of the correct size
        self.quake_array = np.empty(len(quakes), dtype=dtype_arr)

        # populate the array
        for i in range(len(quakes)):
            self.quake_array[i] = (
                quakes[i],
                magnitude_list[i],
                felt_list[i],
                significance_list[i],
                lat_list[i],
                long_list[i]
            )

    def get_filtered_array(self):

        filtered_array = self.quake_array
        if self.location_filter is not None:
            distance_vectorize = np.vectorize(calc_distance)
            location_filter = np.where(
                distance_vectorize(filtered_array['lat'], filtered_array['long'], self.location_filter[0],
                                   self.location_filter[1]) <= self.location_filter[2])
            filtered_array = filtered_array[location_filter]

        if self.property_filter is not None:
            property_filter = np.where((filtered_array['felt'] >= self.property_filter[1]) &
                                       (filtered_array['magnitude'] >= self.property_filter[0]) &
                                       (filtered_array['significance'] >= self.property_filter[2]), True, False)

            filtered_array = filtered_array[property_filter]

        return filtered_array

    def get_filtered_list(self):
        filtered_list = self.get_filtered_array()
        filtered_list = filtered_list['quake']
        return filtered_list

    def set_location_filter(self, latitude, longitude, distance):
        try:
            self.location_filter = (latitude, longitude, distance)
        except ValueError:
            raise ValueError("Invalid/Missing parameters")

    def set_property_filter(self, magnitude=None, felt=None, significance=None):
        if magnitude is None and felt is None and significance is None:
            raise ValueError("Invalid/Missing parameters")
        else:
            if magnitude is None:
                magnitude = 0
            if felt is None:
                felt = 0
            if significance is None:
                significance = 0
            self.property_filter = (magnitude, felt, significance)

    def clear_filter(self):
        self.location_filter = None
        self.property_filter = None


class Quake:
    def __init__(self, magnitude, time, felt, significance, q_type, coords):
        self.mag = magnitude
        self.time = time
        self.felt = felt
        self.sig = significance
        self.q_type = q_type
        self.lat = float(coords[0])
        self.lon = float(coords[1])

    def __str__(self):
        return (f"{self.mag} Magnitude Earthquake, {self.sig} Significance, felt by {self.felt} people in ({self.lat},"
                f" {self.lon})")

    def __repr__(self):
        return self.__str__()

    def get_distance_from(self, latitude, longitude):
        return calc_distance(self.lat, self.lon, latitude, longitude)
