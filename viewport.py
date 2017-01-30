from pygame import Rect

from constants import SCREEN_SIZE
from vector import Vector


class Viewport:

    def __init__(self):
        self.viewport = Rect((0, 0), SCREEN_SIZE)
        self.locked = False
        self.destination = None
        self.speed = 0
        self.on_arrival = None

    def center(self, center, inside):
        if not self.locked:
            self.viewport.center = center
            self.viewport.clamp_ip(inside)

    def get(self):
        return self.viewport

    def lock(self):
        self.locked = True

    def unlock(self):
        self.locked = False

    def move_to(self, destination, speed=100, on_arrival=None):
        self.destination = destination
        self.speed = speed
        self.on_arrival = on_arrival

    def move(self, time_passed):
        if self.destination:
            location = Vector(*self.viewport.topleft)
            vec_to_destination = self.destination - location

            distance_to_destination = vec_to_destination.get_magnitude()
            vec_to_destination.normalize()
            travel_distance = min(distance_to_destination, time_passed * self.speed)
            vec_to_destination.x *= travel_distance
            vec_to_destination.y *= travel_distance
            move = location + vec_to_destination
            self.viewport.topleft = move.x, move.y
            if self.destination == move:
                self.destination = None
                self.on_arrival()
                self.on_arrival = None
