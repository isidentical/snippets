from stl import load_stl, STLObject
from vector import Vector
from matrix import Matrix
from dataclasses import dataclass

@dataclass
class Job:
    x: int
    y: int
    width: int
    height: int
    obj: STLObject
    cammatrix: Matrix

def main(file):
    framew, frameh = 1024, 1024
    stl = load_stl(file)
    cammatrix = Vector(100, 100, 150).look_at(Vector(0, 0, 0))    
    obj = STLObject(Vector(0, 0, 0), stl, Vector(255, 255, 255))
    
    for i in range(1):
        pass
    
if __name__ == '__main__':
    main('40mmcube.stl')
