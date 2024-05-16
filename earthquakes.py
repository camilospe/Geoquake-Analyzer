import math


def calc_distance(lat1, lon1, lat2, lon2):
    """This function will calculate the distance between two coordinates
    the coordinates are given through latitude and longitude (degrees).
    The calculated distance will be in kilometers."""
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


# test cal_distance with values from https://www.omnicalculator.com/other/latitude-longitude-distance
print(f"Testing calculating distance: {calc_distance(27.9881, 86.9250, 40.7484, -73.9857)}  == 12122")
print(f"Testing calculating distance: {calc_distance(48.8566, 2.3522, 50.0647, 19.9450)}  == 1275 ")
