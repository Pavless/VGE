"""Application for visualization of polygon triangulation"""

import math
import sys
from argparse import ArgumentParser

import cairo
import pygame

from helpfunctions import check_points_on_line, check_intersections
from point import Point
from earclipping_anim import EarClippingAnim
from drawing import rgba_to_bgra

from examples import examples_dict

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

def draw_intesections(ctx: cairo.Context, pts):
    ctx.set_line_width(2)
    ctx.set_source_rgba(*rgba_to_bgra(1, 0, 0,1))   
    for p in pts:
        ctx.arc(p[0], p[1],5, 0, 2*math.pi)
        ctx.stroke()

def main():
    print("Instructions:")
    print("####################################################")
    print("f     - starts earclipping")
    print("g     - start earclipping with local edge flipping")
    print("c     - clear input ")
    
    print("1-7   - load examples ")


    print("UP    - increase speed of the animation")
    print("DOWN  - decrease speed of the animation")
    print("LEFT  - run the animation backwards")
    print("RIGHT - run the animation forwards")
    print("SPACE - pause the animation")
    print("####################################################")
    parser = ArgumentParser()
    parser.add_argument("--width", type=int, default=512, help="The width of the application window.")
    parser.add_argument("--height", type=int, default=512, help="The height of the application window.")
    args = parser.parse_args()
    
    width, height = args.width, args.height
    pygame.init()
    window = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    time = 0.0
    total_anim_lenght = 1.0
    speed = 1.0
    speed_diff_update = 1.5
    max_speed = speed_diff_update ** 7
    min_speed = -max_speed
    time_direction = 1.0
    pause = False

    print_speed(speed, pause)

    points_ready = False
    points = []
    intersections = []
    while True:
        
        # set framerate, this call limits the framerate 
        # and returns number of miliseconds passed since the last call
        dt = clock.tick(60)
        
        # update time
        if not pause:
            time += dt * speed * time_direction / total_anim_lenght if (total_anim_lenght != 0) else 1.0
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
            
        if intersections:
            draw_intesections(ctx,intersections)

        ctx.set_line_width(2)
        
        
        # event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.MOUSEBUTTONUP and not points_ready and not intersections:
                pos = pygame.mouse.get_pos()
                points.append(Point(pos[0],pos[1]))

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_f and not intersections and len(points)>=3:
                points,_ = check_points_on_line(points)
                intersections = check_intersections(points)
                if not intersections:
                    points_ready = True
                    anim = EarClippingAnim(points)
                    total_anim_lenght = sum((t for _, t in anim.schedule)) * 1000
                    time = 0.0

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_g and not intersections and len(points)>=3:
                points,_ = check_points_on_line(points)
                intersections = check_intersections(points)
                if not intersections:
                    points_ready = True
                    anim = EarClippingAnim(points, edge_swapping=True)
                    total_anim_lenght = sum((t for _, t in anim.schedule)) * 1000
                    time = 0.0

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                points_ready = False
                points = []
                intersections=[]
            
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                speed *= speed_diff_update
                if speed > max_speed: speed = max_speed
                print_speed(time_direction * speed, pause)


            elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                speed /= speed_diff_update
                if speed < min_speed: speed = min_speed
                print_speed(time_direction * speed, pause)

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                time_direction = -1.0
                print_speed(time_direction * speed, pause)
            
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                time_direction = 1.0
                print_speed(time_direction * speed, pause)
            
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                pause = not pause
                print_speed(time_direction * speed, pause)
                
            elif event.type == pygame.KEYDOWN and (event.key >= ord('1') and event.key <=ord('7')):
                intersections = []
                example_id = event.key-ord('0')-1
                points = (list(examples_dict.values()))[example_id]

        if points_ready:
            anim(ctx, time)

        # Create PyGame surface from Cairo Surface
        buf = surface.get_data()
        image = pygame.image.frombuffer(buf, (width, height), "RGBA")
        # Tranfer to Screen
        screen.blit(image, (0, 0))
        pygame.display.flip()

if __name__ == "__main__":
    main()