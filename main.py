import socket

from math import radians, cos, sin, asin, sqrt, atan2, degrees


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
adress = ("127.0.0.1", 40001)
sock.bind(("127.0.0.1", 40001))

anchor_lat_dd = 0
anchor_long_dd = 0

def calc_distance(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 3959.87433
    return c * r

def calc_bearing (lat1, long1, lat2, long2):
    dLon = (long2 - long1)
    x = cos(radians(lat2)) * sin(radians(dLon))
    y = cos(radians(lat1)) * sin(radians(lat2)) - sin(radians(lat1)) * cos(radians(lat2)) * cos(radians(dLon))
    bearing = atan2(x, y)
    bearing = degrees(bearing)

    return bearing

def dms2dd(lat, direction):
    lat = lat/100
    g = int(lat)
    min = float((lat - g) * 100)
    dd = g + min/60#
    if direction == "S" or direction == "W":
        dd *= -1

    return dd

while True:
    data, addr = sock.recvfrom(1024)

    data_list = [s.strip() + ',' for s in str(data)[2:].split(',') if s.strip()]

    print(data)

    lat_degrees = data_list[3][0:2]
    lat_minutes = data_list[3][2:][0:2]
    lat_seconds = data_list[3][:-1][-5:]
    lat_direction = data_list[4][:-1]

    long_degrees = data_list[5][0:3]
    long_minutes = data_list[5][3:][0:2]
    long_seconds = data_list[5][:-1][-5:]
    long_direction = data_list[6][:-1]

    lat_dms = float(data_list[3][:-1])
    long_dms = float(data_list[5][:-1])

    lat_dd = dms2dd(lat_dms, lat_direction)
    long_dd = dms2dd(long_dms, long_direction)

    if lat_direction == "S":
        lat_dd *= -1
    if long_direction == "W":
        long_dd *= -1

    if anchor_lat_dd == 0 and anchor_long_dd == 0:
        print("Setting anchor...")
        anchor_lat_dd = lat_dd
        anchor_long_dd = long_dd
        print(f"Anchor set at:\n"
              f"Latitude: {lat_dd}\n"
              f"Longitude: {long_dd}")
    else:
        print(f"Distance to anchor: {calc_distance(anchor_long_dd, anchor_lat_dd, long_dd, lat_dd)} ({calc_bearing(anchor_lat_dd, anchor_long_dd, lat_dd, long_dd)} degrees)")




