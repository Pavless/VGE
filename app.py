"""demonstrate pycairo and pygame"""

import math
import sys

import numpy as np
import cairo
import pygame
from PIL import Image

from earclipping import *
from point import Point
from earclipping_anim import EarClippingAnim
import drawing


def draw_polygon_segments(ctx: cairo.Context, vertices):
    """Draws a polygon outline = its segments as lines
    args:
        vertices - a array of points"""
    if len(vertices) < 1:
        raise ValueError("vertices should have at least one point")
    vertex_iter = iter(vertices)
    ctx.move_to(*next(vertex_iter))
    for vertex in vertex_iter:
        ctx.line_to(*vertex)
    ctx.close_path()

def draw(surface):
    ctx = cairo.Context(surface)
    ctx.set_antialias(cairo.Antialias(cairo.Antialias.GOOD))
    
    # fill the background
    ctx.set_source_rgba(*rgba_to_bgra(0,0,1,1)) # corection of byte order
    ctx.rectangle(250, 250, 512, 512)
    ctx.fill()

    # draw triangulation
    ctx.set_line_width(2)
    ctx.set_source_rgb(0.8, 0.8, 0.8)
    # points = [
    #     point.Point(1,1),
    #     point.Point(1,-1),
    #     point.Point(0,0),
    #     point.Point(-1,-1),
    #     point.Point(-1,1),
    #     point.Point(0, 2)
    # ]
    points = [
        Point(0.4,1.9),Point(2.0,-1.3),Point(0.95,-0.5),Point(-0.7,-2.5),Point(-0.3,-1.1), Point(-1.3,-0.2),
        Point(0,0.6),  Point(-1.7,1.0),Point(-2.05,2.7), Point(-0.9,1.25)
    ]
    tmp = rotate_list(points, 8)
    triangles = ear_clipping(tmp)
    for triangle in triangles:
        draw_triangle(ctx, triangle)

    ctx.stroke()


def draw_triangle(ctx: cairo.Context, t):
    v0, v1, v2 = t
    ctx.move_to(v0.x * 65 + 175,v0.y * -65 + 325)
    ctx.line_to(v1.x * 65 + 175,v1.y * -65 + 325)
    ctx.line_to(v2.x * 65 + 175,v2.y * -65 + 325)
    ctx.close_path()

def draw_points(ctx: cairo.Context, pts):
    ctx.set_line_width(2)
    ctx.set_source_rgba(*rgba_to_bgra(0.26, 0.65, 0.77,1))
    


    
    ctx.move_to(pts[0][0], pts[0][1])
    last = ()
    for p in pts:
        ctx.line_to(p[0], p[1])
        ctx.move_to(p[0], p[1])
        last = p
    ctx.stroke()

    ctx.set_source_rgba(*rgba_to_bgra(1,1,1,1))
    ctx.arc(last[0], last[1],3, 0, 2*math.pi)
    ctx.stroke()

    ctx.set_source_rgba(*rgba_to_bgra(0.26, 0.65, 0.77,0.3))
    ctx.move_to(last[0],last[1])
    ctx.line_to(pts[0][0], pts[0][1])
    ctx.stroke()
    

def main():
    print("Instructions...")
    
    width, height = 512, 512
    pygame.init()
    window = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    #points = [
    #    Point(0.4,1.9),Point(2.0,-1.3),Point(0.95,-0.5),Point(-0.7,-2.5),Point(-0.3,-1.1), Point(-1.3,-0.2),
    #    Point(0,0.6),  Point(-1.7,1.0),Point(-2.05,2.7), Point(-0.9,1.25)
    #]
    #points = [point.point_scale(p, 65, 65) for p in points]
    #points = [point.point_add(p, Point(175, 325)) for p in points]

    #print("HASDASd")
    #anim = EarClippingAnim(points)
    #total_anim_lenght = sum((t for _, t in anim.schedule)) * 1000
    time = 0.0
    #print("SDSHASDASd")
    

    points_ready = False
    points = []
    while True:
        
        
         # set framerate, this call limits the framerate 
        # and returns number of miliseconds passed since the last call
        dt = clock.tick(60)
        time += dt
        # render display
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)

        screen = pygame.display.get_surface()

        ctx = cairo.Context(surface)
        ctx.set_antialias(cairo.Antialias(cairo.Antialias.GOOD))
        
        # fill the background
        ctx.set_source_rgba(*rgba_to_bgra(0,0,0,1)) # corection of byte order
        ctx.rectangle(0, 0, width, height)
        ctx.fill()
        
        if not points_ready and points:
            draw_points(ctx,points)

        # draw triangulation
        ctx.set_line_width(2)
        
        
        # event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.MOUSEBUTTONUP and not points_ready:
                pos = pygame.mouse.get_pos()
                points.append(Point(pos[0],pos[1]))

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                points_ready = True
                anim = EarClippingAnim(points)
                total_anim_lenght = sum((t for _, t in anim.schedule)) * 1000

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                points_ready = False
                points = []
            
        
       

        # ctx.set_source_rgba(*rgba_to_bgra(1,1,1,1))
        # drawing.draw_polygon_segments(points)(ctx)
        # ctx.stroke()
        if points_ready:
            anim(ctx, time / total_anim_lenght)

        # Create PyGame surface from Cairo Surface
        buf = surface.get_data()
        image = pygame.image.frombuffer(buf, (width, height), "RGBA")
        # Tranfer to Screen
        screen.blit(image, (0, 0))
        pygame.display.flip()

def rgba_to_bgra(red, green, blue, alpha=1.0):
    return (blue, green, red, alpha)

if __name__ == "__main__":
    main()