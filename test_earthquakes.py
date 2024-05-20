from unittest import TestCase

import numpy as np

import earthquakes
from pathlib import Path
import json


def create_only_10_earthquakes_dictionary():
    """This function will simulate a report from geoson including only 10 earthquakes
    This earthquakes will match the desired format,
    so they are valid for the QuakeData constructor sequence
    """
    dictionary = {}

    features = []

    for i in range(10):
        earthquake = {
            "type": "Feature",
            "properties": {
                "mag": 2.9,
                "time": 1715221312431,
                "felt": 20,
                "sig": 129,
                "magType": "ml",
                "type": "earthquake",
            },
            "geometry": {
                "type": "Point",
                "coordinates": [
                    100,
                    100,
                    0.1
                ]
            },
            "id": "ak0245z16lhr"
        }
        features.append(earthquake)

    dictionary["features"] = features
    return dictionary


def read_earthquakes_dictionary(path):
    """This function will be used for testing purposes
    Will load the earthquakes.geojson file
    and will return a dictionary containing all the dictionaries about earthquakes
    """
    path = Path(path)
    if path.exists():
        geojson_dictionary = json.loads(path.read_text())
    else:
        geojson_dictionary = {}
    return geojson_dictionary


class TestCalculateDistance(TestCase):

    # test cal_distance with values from https://www.omnicalculator.com/other/latitude-longitude-distance
    def test_calculate_distance_valid_answer(self):
        distance = earthquakes.calc_distance(27.9881, 86.9250, 40.7484, -73.9857)
        self.assertEqual(int(distance), 12122)

        distance_2 = earthquakes.calc_distance(48.8566, 2.3522, 50.0647, 19.9450)
        self.assertEqual(int(distance_2), 1275)

    # this test will ensure that the distance between two points of coordinates (0,0) are 0
    def test_calculate_distance_values_0(self):
        distance = earthquakes.calc_distance(0, 0, 0, 0)
        self.assertEqual(distance, 0)

    # this test will ensure that the distance between two points with the same coordinates are 0
    def test_calculate_distance_sames_coordinates(self):
        distance = earthquakes.calc_distance(32.5, 32.5, 32.5, 32.5)
        self.assertEqual(distance, 0)

    # This test will ensure that invalid input for the coordinates will raise a ValueError
    def test_calculate_distance_invalid_coordinates(self):
        with self.assertRaises(ValueError):
            earthquakes.calc_distance('lat1', 0, 0, 0)
        with self.assertRaises(ValueError):
            earthquakes.calc_distance(0, 'lon1', 0, 0)
        with self.assertRaises(ValueError):
            earthquakes.calc_distance(0, 0, 'lat2', 0)
        with self.assertRaises(ValueError):
            earthquakes.calc_distance(0, 0, 0, 'lon2')


class TestQuake(TestCase):

    # This test will ensure the proper creation of the quake object with valid input
    def test_create_quake(self):
        try:
            quake = earthquakes.Quake(2.9, 1715221312431, 1, 120,
                                      "Point", (-151.3096, 62.9726, 24.1))
            self.assertIsInstance(quake, earthquakes.Quake)
        except Exception as e:
            self.fail(f"Creating Quake failed {e}")

    # This test will create a quake object and ensure the string attribute is correct
    def test_quake_string(self):
        quake = earthquakes.Quake(2.9, 1715221312431, 1, 120,
                                  "Point", (-151.3096, 62.9726, 24.1))

        self.assertEqual(quake.__str__(), "2.9 Magnitude Earthquake, 120 Significance, felt by 1 people in "
                                          "(-151.3096, 62.9726)")

    # this test will test the get_distance method in the quake object, distance from himself should be 0
    def test_quake_get_distance_from_himself(self):
        quake = earthquakes.Quake(2.9, 1715221312431, 1, 120,
                                  "Point", (-151.3096, 62.9726, 24.1))
        self.assertEqual(quake.get_distance_from(-151.3096, 62.9726), 0)


class TestQuakeData(TestCase):

    def test_create_quake_data_from_dictionary(self):
        earthquakes_dictionary = read_earthquakes_dictionary("./earthquakes.geojson")
        quake_data = earthquakes.QuakeData(earthquakes_dictionary)
        self.assertIsInstance(quake_data, earthquakes.QuakeData)

    def test_create_quake_data_from_dictionary_have_the_correct_number_of_elements(self):
        earthquakes_dictionary = create_only_10_earthquakes_dictionary()
        quake_data = earthquakes.QuakeData(earthquakes_dictionary)
        self.assertIsInstance(quake_data, earthquakes.QuakeData)
        self.assertEqual(len(quake_data.quake_array.tolist()), 10)

    def test_create_quake_data_from_dictionary_will_ignore_an_invalid_entry(self):
        earthquakes_dictionary = create_only_10_earthquakes_dictionary()

        # Add a valid earthquake, number is 11
        earthquakes_dictionary['features'].append({
            "type": "Feature",
            "properties": {
                "mag": 2.9,
                "time": 1715221312431,
                "felt": 20,
                "sig": 129,
                "magType": "ml",
                "type": "earthquake",
            },
            "geometry": {
                "type": "Point",
                "coordinates": [
                    0,
                    0,
                    0.1
                ]
            },
            "id": "ak0245z16lhr"
        })

        # Add an invalid earthquake
        earthquakes_dictionary['features'].append({
            "type": "Feature",
            "properties": {
            },
            "geometry": {
            },
            "id": "ak0245z16lhr"
        })

        quake_data = earthquakes.QuakeData(earthquakes_dictionary)
        self.assertIsInstance(quake_data, earthquakes.QuakeData)
        self.assertEqual(len(quake_data.quake_array.tolist()), 11)

    def test_unfiltered_array_is_equal_to_complete_array(self):
        earthquakes_dictionary = read_earthquakes_dictionary("./earthquakes.geojson")
        quake_data = earthquakes.QuakeData(earthquakes_dictionary)

        filtered_array = quake_data.get_filtered_array()
        complete_array = quake_data.quake_array

        for i in range(len(filtered_array)):
            self.assertEqual(filtered_array[i], complete_array[i])

    def test_cleared_filter_array_is_equal_to_complete_array(self):
        earthquakes_dictionary = read_earthquakes_dictionary("./earthquakes.geojson")
        quake_data = earthquakes.QuakeData(earthquakes_dictionary)

        quake_data.set_location_filter(100, 100, 5000)
        quake_data.set_property_filter(20, 30, 20)
        filtered_array = quake_data.get_filtered_array()

        filtered_len = len(filtered_array)

        complete_array = quake_data.quake_array

        self.assertNotEqual(filtered_len, len(complete_array))

        quake_data.clear_filter()

        for i in range(len(filtered_array)):
            self.assertEqual(filtered_array[i], complete_array[i])
        self.assertNotEqual(filtered_len, len(quake_data.get_filtered_array()))

    def test_partial_property_filter_is_valid(self):
        earthquakes_dictionary = read_earthquakes_dictionary("./earthquakes.geojson")
        quake_data = earthquakes.QuakeData(earthquakes_dictionary)

        try:
            quake_data.set_property_filter(magnitude=20, felt=40)
            quake_data.set_property_filter(magnitude=20, significance=200)
            quake_data.set_property_filter(felt=49, significance=200)

        except Exception as e:
            self.fail(f"Partial Quake Filter failed {e}")

    def test_property_filter_return_number(self):
        earthquakes_dictionary = create_only_10_earthquakes_dictionary()
        # Add a valid earthquake, number is 11
        earthquakes_dictionary['features'].append({
            "type": "Feature",
            "properties": {
                "mag": 5,
                "time": 1715221312431,
                "felt": 30,
                "sig": 300,
                "magType": "ml",
                "type": "earthquake",
            },
            "geometry": {
                "type": "Point",
                "coordinates": [
                    900,
                    900,
                    0.1
                ]
            },
            "id": "ak0245z16lhr"
        })

        quake_data = earthquakes.QuakeData(earthquakes_dictionary)

        # set filter with returning all values
        quake_data.set_property_filter(0, 0, 0)

        weak_filter_array = quake_data.get_filtered_array()
        weak_filter_list = quake_data.get_filtered_list()

        self.assertEqual(len(weak_filter_array), 11)
        self.assertEqual(len(weak_filter_list), 11)

        # set extreme filter

        quake_data.set_property_filter(99999, 99999, 999999)

        extreme_filter_array = quake_data.get_filtered_array()
        extreme_filter_list = quake_data.get_filtered_list()

        self.assertEqual(len(extreme_filter_array), 0)
        self.assertEqual(len(extreme_filter_list), 0)

        # set strong filter, one of the earthquakes will pass

        quake_data.set_property_filter(5, 30, 300)

        strong_filter_array = quake_data.get_filtered_array()
        strong_filter_list = quake_data.get_filtered_list()

        self.assertEqual(len(strong_filter_array), 1)
        self.assertEqual(len(strong_filter_list), 1)


