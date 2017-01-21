from math import sqrt


class Vector(object):
    """
    Represent a vector of movement
    """

    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def __str__(self):
        return 'Vector({}, {})'.format(self.x, self.y)

    @staticmethod
    def create_from_points(p1, p2):
        return Vector(p2[0]-p1[0], p2[1] - p1[1])

    def get_magnitude(self):
        return sqrt(self.x**2 + self.y**2)

    def normalize(self):
        magnitude = self.get_magnitude()
        if magnitude != 0:
            self.x /= magnitude
            self.y /= magnitude

    def get_direction(self):
        return (-1 if self.x < 0 else 1, -1 if self.y < 0 else 1)

    def __add__(self, rhs):  # right hand side
        return Vector(self.x + rhs.x, self.y + rhs.y)

    def __sub__(self, rhs):
        return Vector(self.x - rhs.x, self.y - rhs.y)

    def __neg__(self):
        return Vector(-self.x , -self.y)

    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)

    def __div__(self, scalar):
        return Vector(self.x / scalar, self.y / scalar)

    def get_distance_to(self, location):
        v = Vector.create_from_points((self.x, self.y), (location.x, location.y))
        return v.get_magnitude()

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not self.__eq__(other)
