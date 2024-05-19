import sys
from pathlib import Path
import json
import numpy as np
import earthquakes


def read_dictionary(path="./earthquakes.geojson"):
    """
    This function will load a dictionary following a path to a json file
    If there are no path provided it will use the earthquakes.geojson by default
    Please ensure default file is located in the same directory as the earthquake_analyser.py script
    :param path: path to a json file
    :return: dictionary with the information from the file
    """
    if path != "./earthquakes.geojson":
        print(f"Received file path to analyze: {path}")

    path = Path(path)

    if path.exists():
        try:
            geojson_dictionary = json.loads(path.read_text())
            print("loaded dictionary correctly")
        except Exception as e:
            print("Could not read provided file")
            raise e
    else:
        raise FileNotFoundError("File doesnt exist")

    return geojson_dictionary


def load_quake_data_from_dictionary(dictionary):
    """
    This function will receive a dictionary contained earthquakes in the geojson format
    Will create a QuakeData object with said dictionary
    If there are no valid earthquakes in the QuakeData object will raise an exception
    If there are at list one valid earthquake it will return the QuakeData
    :param dictionary: Dictionary of earthquakes in geojson format
    :return: QuakeData object
    """
    quake_data = earthquakes.QuakeData(dictionary)
    number_of_valid_earthquakes = len(quake_data.get_filtered_list())
    # Check that at least one valid earthquake was found
    if number_of_valid_earthquakes == 0:
        raise ValueError("No earthquakes found in the provided dictionary")
    else:
        print(f"Dictionary contained {number_of_valid_earthquakes} valid earthquakes")
    return quake_data


def main(argv):
    # Check if a path was provided as a command line argument
    if len(argv) > 0:
        print(f"Received file path to analyze: {argv[0]}")
        geojson_dictionary = read_dictionary(argv[0])
    else:
        geojson_dictionary = read_dictionary()

    load_quake_data_from_dictionary(geojson_dictionary)

    while True:
        option = input("""
           1. Set Location Filter
           2. Set Property Filter
           3. Clear Filters
           4. Display Quakes
           5. Display Exceptional Quakes
           6. Display Magnitude Stats
           7. Plot Quake Map
           8. Plot Magnitude Chart
           9. Quit
        Please select an option (1-9)
           """)
        sys.exit()


if __name__ == "__main__":
    main(sys.argv[1:])
