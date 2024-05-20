import math
import json
import numpy as np
from pathlib import Path


def ensure_numeric(value):
    """
    This method will ensure a value is numeric
    :param value: a value
    :return: said value  if its numeric.
    """
    if isinstance(value, (int, float)):
        return value
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"{value} is not a numeric value")


def calc_distance(lat1, lon1, lat2, lon2):
    """
    This function will calculate the distance between two coordinates
    the coordinates are given through latitude and longitude (degrees).
    The distance is calculated used the haversine formula
    The calculated distance will be in kilometers.
    :param lat1: Latitude of the first point.
    :param lon1: Longitude of the first point.
    :param lat2: Latitude of the second point.
    :param lon2: Longitude of the second point.
    :return: distance in kilometers.
    """
    # Ensure the coordinates are numeric
    lat1 = ensure_numeric(lat1)
    lon1 = ensure_numeric(lon1)
    lat2 = ensure_numeric(lat2)
    lon2 = ensure_numeric(lon2)

    _earth_radius = 6_371_000

    # apply haversine formula
    lat1_radian = lat1 * math.pi / 180
    lat2_radian = lat2 * math.pi / 180

    lat_variation = (lat2 - lat1) * math.pi / 180
    long_variation = (lon2 - lon1) * math.pi / 180

    a = math.pow(math.sin(lat_variation / 2), 2) + math.cos(lat1_radian) * math.cos(lat2_radian) * math.pow(
        math.sin(long_variation / 2), 2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance_meters = _earth_radius * c

    # convert distance to kilometers
    distance_kms = distance_meters / 1000
    return distance_kms


def filter_invalid_earthquakes(earthquakes, magnitude_list, felt_list, significance_list, lat_list, long_list):
    """
    This function receives a dictionary of earthquakes
    and discards the invalid ones. Valid earthquakes are those
    that meet the following criteria:

    1. The 'geometry' type is 'Point'.
    2. The 'type' is 'Feature'.
    3. The coordinates are in a tuple format (validated by the coordinate_is_tuple function).
    4. The 'properties' dictionary contains the keys: 'mag', 'time', 'felt', 'sig', 'type', and 'magType'.

    Valid earthquakes will be added in a list of Quake objects
    :param earthquakes: dictionary of earthquakes
    :param magnitude_list: an empty list to populate with magnitudes
    :param felt_list: an empty list to populate with felts
    :param significance_list: an empty list to populate with significances
    :param lat_list: an empty list to populate with latitudes
    :param long_list: an empty list to populate with longitudes
    :return: a list of valid earthquakes
    """

    valid_earthquakes = []

    # grab the earthquakes from the dictionary
    for earthquake in earthquakes['features']:

        # valid earthquake must have the type, geometry -> type,
        # mag, felt, sig, type, magType, and geometry -> coordinates fields
        if 'coordinates' in earthquake['geometry']:
            if earthquake['geometry']['type'] == "Point" and earthquake['type'] == "Feature":

                # check if coordinates is a tuple of numbers
                if coordinate_is_tuple(earthquake):

                    # check no missing fields
                    if ('mag' in earthquake['properties'] and
                            'time' in earthquake['properties'] and
                            'felt' in earthquake['properties'] and
                            'sig' in earthquake['properties'] and
                            'type' in earthquake['properties'] and
                            'magType' in earthquake['properties'] and
                            isinstance(earthquake['properties']['felt'], (int, float))):
                        valid_earthquakes.append(earthquake)
    # empty list to populate with valid earthquakes
    quakes_list = []

    # populate earthquake and field lists
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

        # if operation fails, continue to next entry
        except ValueError as e:
            continue
    # return earthquake list
    return quakes_list


def coordinate_is_tuple(earthquake):
    """
    This function will check if the coordinates are a valid tuple
    :param earthquake: earthquake dictionary
    :return: True if is a tuple of numeric values
    """
    coordinates = earthquake['geometry']['coordinates']

    # must be a tuple with 3 numbers
    if isinstance(coordinates, (tuple, list)) and len(coordinates) == 3:
        for coordinate in coordinates:
            if not isinstance(coordinate, (int, float)):
                return False
        return True
    else:
        return False


class QuakeData:
    def __init__(self, earthquakes):

        # empty field lists
        magnitude_list = []
        felt_list = []
        significance_list = []
        lat_list = []
        long_list = []

        # set default filters
        self.location_filter = None
        self.property_filter = None

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
        """
        This will filter the earthquakes based on the location and property filters
        :return: np array of filtered earthquakes
        """

        # get all earthquakes
        filtered_array = self.quake_array

        # if there is a location filter apply
        if self.location_filter is not None:

            # vectorize function so its usable by numpy
            distance_vectorize = np.vectorize(calc_distance)

            # np array with True if the location to the filter point is less or equal than the requested distance
            location_filter = np.where(
                distance_vectorize(filtered_array['lat'], filtered_array['long'], self.location_filter[0],
                                   self.location_filter[1]) <= self.location_filter[2])
            # update the array with the filter
            filtered_array = filtered_array[location_filter]

        # if there is a property filter apply
        if self.property_filter is not None:
            # np array with True if the felt, mag, and significance of the earthquakes are larger than the filter
            property_filter = np.where((filtered_array['felt'] >= self.property_filter[1]) &
                                       (filtered_array['magnitude'] >= self.property_filter[0]) &
                                       (filtered_array['significance'] >= self.property_filter[2]), True, False)

            # apply filter
            filtered_array = filtered_array[property_filter]

        # return np array after the two optional filters
        return filtered_array

    def get_filtered_list(self):
        """
        This function will return a list of Quake objects after they passed the filters
        :return: list of Quake objects
        """

        # call get_filtered_array() to apply filters
        filtered_list = self.get_filtered_array()

        # convert the 'quake' column to a list of Quakes
        filtered_list = filtered_list['quake']
        return filtered_list

    def set_location_filter(self, latitude, longitude, distance):
        """
        This function will set a maximum distance to a point for the earthquakes
        :param latitude: Latitude of the point
        :param longitude: longitude of the point
        :param distance: Maximum distance to the point (kms)
        """

        # try to set the location filter (will need all parameters)
        try:
            # ensure the values are numeric
            ensure_numeric(latitude)
            ensure_numeric(longitude)
            ensure_numeric(distance)

            self.location_filter = (latitude, longitude, distance)
        except ValueError:
            raise ValueError("Invalid/Missing parameters")

    def set_property_filter(self, magnitude=None, felt=None, significance=None):
        """
        This function will set a minimum magnitude, felt, and significance criteria for the earthquakes
        :param magnitude: magnitude of the earthquake
        :param felt: number of reports
        :param significance: number of how significant was the earthquake
        """
        # parameters not provided are set to 0. also count the number of valid parameters
        invalid_count = 0
        if magnitude is None:
            magnitude = 0
            invalid_count += 1
        else:
            try:
                magnitude = float(magnitude)
            except ValueError:
                magnitude = 0
                invalid_count += 1

        if felt is None:
            felt = 0
            invalid_count += 1
        else:
            try:
                felt = float(felt)
            except ValueError:
                felt = 0
                invalid_count += 1

        if significance is None:
            significance = 0
            invalid_count += 1
        else:
            try:
                significance = float(significance)
            except ValueError:
                significance = 0
                invalid_count += 1

        # if all parameters are not valid then raise the exception
        if invalid_count >= 3:
            raise ValueError("Invalid/Missing parameters")

        # set the filter
        else:
            self.property_filter = (magnitude, felt, significance)

    def clear_filter(self):
        """
        This function will clear the location and property filters
        """
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
