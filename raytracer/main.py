from stl import load_stl, STLObject
from vector import Vector
from matrix import Matrix
from dataclasses import dataclass, field
from math import tan, pi
from ray import Ray, Hit

@dataclass
class Job:
    x: int
    y: int
    width: int
    height: int
    framew: int
    frameh: int
    framebuffer: Matrix
    obj: STLObject
    cammatrix: Matrix

def facing_ratio_shader(px, py, ray_dir, job):
    origin = Vector(*job.cammatrix[3][:3])
    cam_ray = Ray(origin, ray_dir)
    
    hit = Hit()
    if cam_ray.intersects_object(job.obj, hit):
        print(1)
        job.framebuffer[px][py] * 5

def render(job):
    inv_width = 1 / job.framew
    inv_height = 1 / job.frameh
    
    fov = 90
    aspectratio = job.framew / job.frameh
    angle = tan(pi * fov * 0.5 / 180.0)
    
    for y in range(int(job.height)):
        for x in range(job.width):
            cam_forward = Vector(*job.cammatrix[1][:3])
            u = Vector(*job.cammatrix[0][:3])
            v = Vector(*job.cammatrix[2][:3])
            w = cam_forward * -1
            
            xx = (2 * ((x + 0.5) * inv_width) - 1)/2 * angle * aspectratio
            yy = (1 - 2 * ((y + 0.5) * inv_height))/2 * angle
            xp = Vector.from_scalar(xx)
            yp = Vector.from_scalar(yy)
            
            direction = (w + (xp * u)) + (yp * v)
            direction = direction.normalize()
            
            facing_ratio_shader(x, y, direction, job)
    
    return None

def main(file):
    stl = load_stl(file)
    
    framew, frameh = 16, 16
    cammatrix = Vector(100, 100, 150).look_at(Vector(0, 0, 0))    
    obj = STLObject(Vector(0, 0, 0), stl, Vector(255, 255, 255))
    framebuffer = Matrix(frameh, framew, fill_with = (Vector, 0, 0, 0))
    global job
    
    job_amount = 1
    for i in range(job_amount):
        job = Job(
            x = 0,
            y = frameh / job_amount,
            width = framew,
            height = (i + 1) * (frameh/job_amount),
            framew = framew,
            frameh = frameh, 
            framebuffer = framebuffer,
            obj = obj,
            cammatrix = cammatrix            
        )
        
        render(job)
    
    return job
    
    
    
if __name__ == '__main__':
    job = main('40mmcube.stl')
    for y in range(int(job.frameh)):
        for x in range(job.framew):
            pass
