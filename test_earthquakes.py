from unittest import TestCase
import earthquakes
from pathlib import Path
import json


def read_earthquakes_dictionary():
    """This function will be used for testing purposes
    Will load the earthquakes.geojson file
    and will return a dictionary containing all the dictionaries about earthquakes
    """
    path = Path("./Data/earthquakes.geojson")
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
