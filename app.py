"""demonstrate pycairo and pygame"""

import math
import sys

import cairo
import pygame

from earclipping import *
from point import Point

def draw(surface):
    x, y, radius = (250, 250, 200)
    ctx = cairo.Context(surface)
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


def input(events):
    for event in events:
        if event.type == pygame.QUIT:
            print(event)
            sys.exit(0)
        else:
            print(event)


def main():
    width, height = 512, 512
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)

    pygame.init()
    pygame.display.set_mode((width, height))
    screen = pygame.display.get_surface()

    draw(surface)

    # Create PyGame surface from Cairo Surface
    buf = surface.get_data()
    image = pygame.image.frombuffer(buf, (width, height), "ARGB")
    # Tranfer to Screen
    screen.blit(image, (0, 0))
    pygame.display.flip()

    while True:
        input(pygame.event.get())


if __name__ == "__main__":
    main()