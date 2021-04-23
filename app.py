"""demonstrate pycairo and pygame"""

import math
import sys
from argparse import ArgumentParser

import numpy as np
import cairo
import pygame
from PIL import Image

from earclipping import *
from point import Point
from earclipping_anim import EarClippingAnim

def print_speed(speed, pause):
    sys.stdout.write("\033[K")
    if pause: 
        print(f"Current speed: PAUSED", end="\r")
    else:
        print(f"Current speed: {speed}", end="\r")

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
    print("Instructions:")
    print("##############################################")
    print("f     - starts earclipping")
    print("UP    - increase speed of the animation")
    print("DOWN  - decrease speed of the animation")
    print("SPACE - pause the animation")
    print("##############################################")
    
    width, height = 512, 512
    pygame.init()
    window = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    time = 0.0
    total_anim_lenght = 1.0
    speed = 1.0
    max_speed = 8.0
    min_speed = -8.0
    speed_diff_update = 0.5
    pause = False

    print_speed(speed, pause)

    points_ready = False
    points = []
    while True:
        
        
        # set framerate, this call limits the framerate 
         # set framerate, this call limits the framerate 
        # set framerate, this call limits the framerate 
        # and returns number of miliseconds passed since the last call
        dt = clock.tick(60)
        
        # update time
        if not pause:
            time += dt * speed / total_anim_lenght if (total_anim_lenght != 0) else 1.0
        if time > 1.0: time = 1.0
        if time < 0: time = 0


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
                time = 0.0

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                points_ready = False
                points = []
            
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                speed += speed_diff_update
                if speed > max_speed: speed = max_speed
                print_speed(speed, pause)


            elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                speed -= speed_diff_update
                if speed < min_speed: speed = min_speed
                print_speed(speed, pause)

            
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                pause = not pause
                print_speed(speed, pause)


            
        
       

        # ctx.set_source_rgba(*rgba_to_bgra(1,1,1,1))
        # drawing.draw_polygon_segments(points)(ctx)
        # ctx.stroke()
        if points_ready:
            anim(ctx, time)

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