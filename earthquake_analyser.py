import sys
from pathlib import Path
import json
import numpy as np
import earthquakes
import matplotlib.pyplot as plt


def read_dictionary(path="./earthquakes.geojson"):
    """
    This function will load a dictionary following a path to a json file
    If there are no path provided it will use the earthquakes.geojson by default
    Please ensure default file is located in the same directory as the earthquake_analyser.py script
    :param path: path to a json file
    :return: dictionary with the information from the file
    """

    path = Path(path)

    # check if path directs to a file
    if path.exists():
        # Try to load the json content to a dictionary
        try:
            geojson_dictionary = json.loads(path.read_text())
            print("loaded dictionary correctly")

        except Exception as e:
            print("Could not read provided file")
            sys.exit()

    else:
        print("File doesnt exist")
        sys.exit()

    # return dictionary
    return geojson_dictionary


def load_quake_data_from_dictionary(dictionary):
    """
    This function will receive a dictionary contained earthquakes in the geojson format
    Will create a QuakeData object with said dictionary
    If there are no valid earthquakes in the QuakeData object will provide a message and exit
    If there are at list one valid earthquake it will return the QuakeData
    :param dictionary: Dictionary of earthquakes in geojson format
    :return: QuakeData object
    """

    # create a new instance of the QuakeData class
    quake_data = earthquakes.QuakeData(dictionary)

    # Check that at least one valid earthquake was found
    number_of_valid_earthquakes = len(quake_data.get_filtered_list())
    if number_of_valid_earthquakes == 0:
        print("No earthquakes found in the provided dictionary")
        sys.exit()
    else:
        print(f"Dictionary contained {number_of_valid_earthquakes} valid earthquakes")
    return quake_data


def set_location_filter(quake_data):
    """
    This method will set a filter of how far the earthquakes can be from a specific location
    :param quake_data: QuakeData object
    """
    print("""

        To set the a new location filter please provide all of the following values:

        Latitude: Decimal degrees latitude. Negative values for southern latitudes. Typical Values [-90.0, 90.0]
        Longitude: Decimal degrees longitude. Negative values for western longitudes. Typical Values [-180.0, 180.0]
        Distance: The maximum distance in kilometers to the (latitude, longitude) location Typical Values: [0, 10000]
    """)

    # get user parameter
    user_latitude = input("Latitude: ")
    user_longitude = input("Longitude: ")
    user_distance = input("Distance: ")

    # sanitize
    user_latitude = user_latitude.strip()
    user_longitude = user_longitude.strip()
    user_distance = user_distance.strip()

    # ensure the values are valid if it cant make the conversion and set filter it will display an error
    try:
        user_latitude = float(user_latitude)
        user_longitude = float(user_longitude)
        user_distance = float(user_distance)

        quake_data.set_location_filter(user_latitude, user_longitude, user_distance)

        print("successfully set the location filter")
    except ValueError:
        print("Please enter a valid latitude, longitude and distance values")


def set_property_filter(quake_data):
    """
    This method will set up a property filter for the earthquakes
    The user must provide at least one valid parameter
    :param quake_data: QuakeData Object
    """
    print("""
    
        To set the a new property filter please provide at least one of the following values:
        
        Significance: A number describing how significant the event is. Larger numbers indicate a more significant event. Typical values: [0, 1000]
        Felt: The total number of felt reports submitted to the DYFI? system. Typical Values: [0.0, 180.0]
        Magnitude: The magnitude for the event. Typical Values: [-1.0, 10.0]
        
        If you wish to skip any of these values just press enter without any input
    """)

    # get parameters
    user_significance = input("significance: ")
    user_felt = input("felt: ")
    user_magnitude = input("magnitude: ")

    # Sanitize the input

    user_significance = user_significance.strip()
    user_felt = user_felt.strip()
    user_magnitude = user_magnitude.strip()

    invalid_count = 0

    # check if the values are numeric
    try:
        user_significance = float(user_significance)
    except ValueError:
        user_significance = None
        invalid_count += 1

    try:
        user_felt = float(user_felt)
    except ValueError:
        user_felt = None
        invalid_count += 1

    try:
        user_magnitude = float(user_magnitude)
    except ValueError:
        user_magnitude = None
        invalid_count += 1

    # if the user didnt provide at least one parameter send error
    if invalid_count == 3:
        print("No valid significance/felt/magnitude values found \nUnable to set property filter")

    # if the user did provide at least one parameter set the filter
    else:
        quake_data.set_property_filter(user_magnitude, user_felt, user_significance)
        print("Successfully set property filter")


def clear_filters(quake_data):
    """
    This method will clear both the property and the location filters
    :param quake_data: QuakeData object
    """
    try:
        quake_data.clear_filter()
        print("Successfully cleared filters")
    except Exception as e:
        print("Unable to clear filters")


def display_filtered_quakes(quake_data):
    """
    This method will display the earthquakes after they were passed the location and property filters
    :param quake_data: QuakeData Object
    """

    # display if at least one earthquake passes the filters
    if len(quake_data.get_filtered_list()) > 0:
        for quake in quake_data.get_filtered_list():
            print(quake)
    else:
        print("No earthquakes records that passes current filters")


def display_exceptional_quakes(quake_data):
    """
    The following method will display a list of earthquakes with a magnitude over 1 std deviation from the mean
    :param quake_data:  QuakeData object
    """
    # get filtered array
    filtered_array = quake_data.get_filtered_array()

    # get mean and std dev
    std = np.std(filtered_array['magnitude'])
    mean = np.mean(filtered_array['magnitude'])

    # get a list of earthquakes with a magnitude over 1 std deviation from the mean
    exceptional_quakes = np.where(filtered_array['magnitude'] > (mean + std))
    exceptional_quakes = filtered_array[exceptional_quakes]

    # Display the list
    for quake in exceptional_quakes['quake']:
        print(quake)


def display_magnitude_stats(quake_data):
    """
    This method will display the mean, standard deviation, mode, and median of the magnitude of the filtered earthquakes
    :param quake_data: QuakeData object
    """

    # get filtered earthquakes
    filtered_array = quake_data.get_filtered_array()

    # calculate stats
    mean = np.mean(filtered_array['magnitude'])
    std = np.std(filtered_array['magnitude'])
    median = np.median(filtered_array['magnitude'])

    # round down the magnitude
    round_mag = filtered_array['magnitude'].round().astype(int)

    # calculate the mode
    mode = np.argmax(np.bincount(round_mag))

    # display stats
    print("Magnitude Statistics")
    print(f"Mean: {mean:.2f}")
    print(f"Std Dev: {std:.2f}")
    print(f"Median: {median:.2f}")
    print(f"Mode: {mode}")


def display_quake_map(quake_data):
    """
    This method will create a scatter map. Where the X is lat, Y is lon
    and the size of the marker represents the magnitude of the earthquake(multiplied by 25 so its visible)
    :param quake_data: QuakeData object
    """
    # force new window
    plt.figure()

    # get filtered array
    filtered_array = quake_data.get_filtered_array()

    # plot the scatter map
    plt.scatter(filtered_array['lat'], filtered_array['long'], s=filtered_array['magnitude'] * 25,
                edgecolors='black', marker='o',
                label='Earthquake Magnitude')

    plt.xlabel('Latitude (degrees)')
    plt.ylabel('Longitude (degrees)')
    plt.title('Earthquakes Magnitude')

    # dont need to close the scatter map to continue using the script
    plt.show(block=False)


def display_magnitude_chart(quake_data):
    """
    This function will display a bar char where each bar will show the number of earthquakes for a magnitude (rounded down)
    the scatter bar will be displayed in a new window.
    :param quake_data: QuakeData object
    """
    # force new window
    plt.figure()

    # get array and round down
    filtered_array = quake_data.get_filtered_array()
    round_mag = filtered_array['magnitude'].round().astype(int)

    # get the different magnitudes at their counts
    magnitude, counts = np.unique(round_mag, return_counts=True)

    # plot the  bar chart
    plt.bar(magnitude, counts, color='cyan', edgecolor='black')
    plt.title('Earthquake Magnitude')
    plt.xlabel('Magnitude')
    plt.ylabel('N of Earthquakes')
    plt.show(block=False)


def main(argv):
    # Check if a path was provided as a command line argument
    if len(argv) > 0:
        print(f"\nReceived file path to analyze: {argv[0]}")
        geojson_dictionary = read_dictionary(argv[0])
    else:
        geojson_dictionary = read_dictionary()

    quake_data = load_quake_data_from_dictionary(geojson_dictionary)

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

        option.strip()
        if option == "1":
            set_location_filter(quake_data)
        elif option == "2":
            set_property_filter(quake_data)
        elif option == "3":
            clear_filters(quake_data)
        elif option == "4":
            display_filtered_quakes(quake_data)
        elif option == "5":
            display_exceptional_quakes(quake_data)
        elif option == "6":
            display_magnitude_stats(quake_data)
        elif option == "7":
            display_quake_map(quake_data)
        elif option == "8":
            display_magnitude_chart(quake_data)
        elif option == "9":
            sys.exit()
        else:
            print("Invalid option, please select one of the options by choosing the number accordingly")


if __name__ == "__main__":
    main(sys.argv[1:])
