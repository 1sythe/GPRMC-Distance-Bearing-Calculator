# visualization was mad using pygame (lmao)

import sys
import socket
import pygame

from pygame.locals import *
from pygame import Vector2
from math import radians, cos, sin, asin, sqrt, atan2, degrees, pi


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
adress = ("127.0.0.1", 40001)
sock.bind(("127.0.0.1", 40001))

pygame.init()
screen = pygame.display.set_mode((600, 600))
screen.fill((215, 217, 215))
icon = pygame.image.load("assets/graphics/compass.png")
pygame.display.set_icon(icon)

clock = pygame.time.Clock()
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


def miles2meters(miles):
    return miles * 1609.344


def degrees2radians(degrees):
    return degrees*(pi/180)


class GRAPHIC:
    def __init__(self):
        self.anchor_lat_dms = None
        self.anchor_long_dms = None
        self.anchor_long_dd = None
        self.anchor_lat_dd = None

        self.anchored = False
        self.meters = 0

        self.anchor = pygame.image.load("assets/graphics/anchor.png").convert_alpha()
        self.ship = pygame.image.load("assets/graphics/ship-wheel.png").convert_alpha()

    def set_anchor(self, lat_dd, long_dd, lat_dms, long_dms):
        self.anchor_lat_dd = lat_dd
        self.anchor_long_dd = long_dd
        self.anchor_lat_dms = lat_dms
        self.anchor_long_dms = long_dms

        self.anchored = True

    def draw_anchor(self):
        anchor = pygame.transform.scale(self.anchor, (40, 40))
        rect = anchor.get_rect(center=screen.get_rect().center)

        screen.blit(anchor, rect)

    def draw_ship(self, meters, radians):
        #ship = pygame.transform.scale(self.ship, (30, 30))
        ship_pos = Vector2(300, 300)

        ship_pos.x = ship_pos.x + (meters*cos(radians))
        ship_pos.y = ship_pos.y + (meters*sin(radians))

        #ship_rect = pygame.Rect((ship_pos.x, ship_pos.y), (30, 30))
        #ship_rect.centerx = ship_pos.x
        #ship_rect.centery = ship_pos.y

        pygame.draw.circle(screen, (91, 158, 71), (ship_pos.x, ship_pos.y), 4)
        #screen.blit(ship, ship_rect)

    def update_title(self, title: str):
        pygame.display.set_caption(title)

    def draw_circles(self):
        pygame.draw.circle(screen, (230, 119, 39), (300, 300), (50+2)*2, width=3)
        pygame.draw.circle(screen, (230, 87, 39), (300, 300), (100 + 2) * 2, width=3)
        pygame.draw.circle(screen, (230, 39, 39), (300, 300), (140 + 2) * 2, width=3)

        font = pygame.font.Font("assets/fonts/Poppins-Medium.ttf", 12)

        first_dis = f"50m"
        second_dis = "100m"
        third_dis = "140m"

        if 160 < self.meters < 1500:
            first_dis = "500m"
            second_dis = "1km"
            third_dis = "1.4km"
        elif self.meters > 1500:
            first_dis = "5km"
            second_dis = "10km"
            third_dis = "14km"

        first = font.render(first_dis, True, (230, 119, 39))
        first_pos = first.get_rect()
        first_pos.centerx = screen.get_rect().centerx
        first_pos.centery = 188

        second = font.render(second_dis, True, (230, 87, 39))
        second_pos = second.get_rect()
        second_pos.centerx = screen.get_rect().centerx
        second_pos.centery = 88

        third = font.render(third_dis, True, (230, 39, 39))
        third_pos = third.get_rect()
        third_pos.centerx = screen.get_rect().centerx
        third_pos.centery = 8

        screen.blit(first, first_pos)
        screen.blit(second, second_pos)
        screen.blit(third, third_pos)


graphic = GRAPHIC()


while True:
    data, addr = sock.recvfrom(1024)

    data_list = [s.strip() + ',' for s in str(data)[2:].split(',') if s.strip()]

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
        print(f"Distance to anchor: {calc_distance(anchor_long_dd, anchor_lat_dd, long_dd, lat_dd)} miles - {miles2meters(calc_distance(anchor_long_dd, anchor_lat_dd, long_dd, lat_dd))} meters ({calc_bearing(anchor_lat_dd, anchor_long_dd, lat_dd, long_dd)} degrees)")

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        elif event == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                print("esc")

    screen.fill((255, 255, 255))

    graphic.draw_anchor()

    meters = miles2meters(calc_distance(anchor_long_dd, anchor_lat_dd, long_dd, lat_dd))

    graphic.meters = meters

    if meters < 160:
        meters *= 2
    elif meters < 1500:
        meters = meters/10*2
    else:
        meters = meters/100*2

    graphic.draw_ship(
        meters=meters,
        radians=degrees2radians(calc_bearing(anchor_lat_dd, anchor_long_dd, lat_dd, long_dd) - 90)
    )
    graphic.draw_circles()
    graphic.update_title(f"Distance to anchor: {miles2meters(calc_distance(anchor_long_dd, anchor_lat_dd, long_dd, lat_dd))} meters ({calc_bearing(anchor_lat_dd, anchor_long_dd, lat_dd, long_dd)} degrees)")

    pygame.display.update()
    clock.tick(60)
