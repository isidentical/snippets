import operator
from math import sqrt
from dataclasses import dataclass
from itertools import repeat

from matrix import Matrix

@dataclass
class Vector:
    x: int
    y: int
    z: int

    def __post_init__(self):
        for attr, value in vars(self).items():
            if isinstance(value, tuple):
                setattr(self, attr, value[0])

    @classmethod
    def from_scalar(cls, scalar):
        return cls(*repeat(scalar, 3))

    def __math__(self, other, op):
        if not isinstance(other, self.__class__):
            other = self.__class__(*repeat(other, 3))

        return self.__class__(
            *(
                op(item1, item2)
                for item1, item2 in zip(vars(self).values(), vars(other).values())
            )
        )

    def __add__(self, other):
        return self.__math__(other, operator.add)

    def __sub__(self, other):
        return self.__math__(other, operator.sub)

    def __mul__(self, other):
        return self.__math__(other, operator.mul)

    def __truediv__(self, other):
        return self.__math__(other, operator.truediv)

    def __floordiv__(self, other):
        return self.__math__(other, operator.floordiv)

    def length(self):
        return sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def cross_prod(self, other):
        return self.__class__(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    
    def dot_prod(self, other):
        return sum(vars(self * other).values())
    
    def normalize(self):
        return self / self.length()
    
    def look_at(self, other):
        tmp = self.__class__(0, 0, 1)
        forward = (self - other).normalize()
        right = tmp.normalize().cross_prod(forward)
        up = forward.cross_prod(right)
        
        camtoworld = Matrix(4, 4)
        
        def set_items(level, vector):
            nonlocal camtoworld

            for n, item in enumerate(vars(vector).values()):
                camtoworld[level][n] = item
        
        set_items(0, right)
        set_items(1, forward)
        set_items(2, up)
        set_items(3, other)
        
        return camtoworld

