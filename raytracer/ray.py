from dataclasses import dataclass, field
from vector import Vector

EPSILON = 1e-07
ZERO_VECTOR = field(default_factory = lambda: Vector.from_scalar(0))

@dataclass
class Ray:
    origin: Vector
    direction: Vector

    def intersects_triangle(self, triangle, hit):
        print(self.direction, self.origin)
        vertex0, vertex1, vertex2 = triangle.points

        edge1 = vertex1 - vertex0
        edge2 = vertex2 - vertex0

        h = self.direction.cross_prod(edge2)
        a = edge1.dot_prod(h)
        
        if EPSILON > a > -EPSILON:
            return False

        f = 1.0 / a
        s = self.origin - vertex0
        u = f * s.dot_prod(h)
        
        if u < 0 or u > 1:
            return False

        q = s.cross_prod(edge1)
        v = f * self.direction.dot_prod(q)
        if v < 0 or u + v > 1:
            return False

        t = f * edge2.dot_prod(q)
        if t > EPSILON:
            hit.intersect_point = ray.origin + (ray.direction * t)
            return True
        return False

    def intersects_object(self, obj, hit):
        nearest_out_intersection_point = Vector(
            float("inf"), float("inf"), float("inf")
        )

        for tri in obj.stlfile.triangles:
            if self.intersects_triangle(tri, hit):
                if (hit.intersect_point - self.origin).length() < (
                    nearest_out_intersection_point - self.origin
                ).length():
                    nearest_out_intersection_point = hit.intersect_point
                    hit.normal = tri.normal

        if nearest_out_intersection_point.x != float("inf"):
            hit.intersection_point = nearest_out_intersection_point
            return True
        return False


@dataclass
class Hit:
    intersect_point: Vector = ZERO_VECTOR
    normal: Vector = ZERO_VECTOR
