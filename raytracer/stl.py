from struct import Struct, unpack
from dataclasses import dataclass
from vector import Vector
from typing import Tuple, Sequence

POSSIBLE_ASCII = 50000
F4_LE = Struct("<f")
    
def read_f4(buf):
    return F4_LE.unpack(buf.read(4))

@dataclass
class STLTriangle:
    normal: Vector
    points: Tuple[Vector, Vector, Vector]
    byte_count: int
    
    @classmethod
    def from_buf(cls, buf):
        points = []
        for _ in range(12):
            points.append(read_f4(buf))
        
        points = zip(*[iter(points)] * 3)
        vectors = []
        for point in points:
            vectors.append(Vector(*point))
        
        normal = vectors.pop(0)
        points = vectors
        return cls(normal, points, 0)

@dataclass
class STLFile:
    header: bytes
    triangles: Sequence[STLTriangle]

@dataclass
class STLObject:
    pos: Vector
    stlfile: STLFile
    color: Vector

def load_stl(path):
    with open(path, "rb") as f:
        header = f.read(80)
        total_triangles = int.from_bytes(f.read(4), 'little')
        
        triangles = []
        for _ in range(total_triangles):
            triangles.append(STLTriangle.from_buf(f))
    
    return STLFile(header, triangles)
        

if __name__ == '__main__':
    from pprint import pprint
    file = load_stl('40mmcube.stl')
    pprint(file.triangles)
