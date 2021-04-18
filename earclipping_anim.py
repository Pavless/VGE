import cairo
import math
from point import Point
import drawing

import point

class DoublyLinkedItem:
    def __init__(self, value):
        self.value = value
        self.next = None
        self.prev = None

class DoublyLinkedList:
    def __init__(self, first_element_value):
        first = DoublyLinkedItem(first_element_value)
        first.next = first
        first.prev = first

        self.head = first
        self.active = first
        self.size = 1

    def move_right(self):
        self.active = self.active.next
    
    def move_left(self):
        self.active = self.active.prev

    def insert_end(self, value):
        new_item = DoublyLinkedItem(value)
        
        last = self.head.prev
        
        new_item.next = self.head
        new_item.prev = last
        self.head.prev = new_item
        last.next = new_item
        self.size += 1

    def remove(self):
        if self.size <= 1:
            raise ValueError("Invalid operation")
        if self.active == self.head:
            self.head = self.head.next
        self.active.next.prev = self.active.prev
        self.active.prev.next = self.active.next
        self.active = self.active.prev
        self.size -= 1
    
    def __len__(self):
        return self.size
    
    def enumerate_values(self):
        values = []
        curr = self.head
        for _ in range(len(self)):
            values.append(curr.value)
            curr = curr.next
        return values


class EarClippingAnim:
    def __init__(self, vertices):
        # build the animation schedule
        self.schedule = self._build_schedule(vertices)
        print(self.schedule)
        for item in self.schedule:
            print(item)
        anims = [anim for anim, _ in self.schedule]
        timeline = [time for _, time in self.schedule]
        self.anim = drawing.combine_anims(anims, timeline)

    def __call__(self, ctx, time):
        self.anim(ctx, time)

    def _build_schedule(self, vertices):
        """Build a animation schedule by walking the steps of the algorithm"""
        if len(vertices) < 3:
            raise ValueError("vertices should have at least 3 items")
        
        vertex_count = len(vertices)
        vertex_radius = 5
        schedule = []

        # initialize linked list containing vertices
        vertex_iter = iter(vertices)
        vertices = DoublyLinkedList(next(vertex_iter))
        for vertex in vertex_iter:
            vertices.insert_end(vertex)

        # draw outline of the polygon
        schedule.append(
            (drawing.create_alpha_color_anim(0.26, 0.65, 0.77, drawing.draw_polygon_segments(vertices.enumerate_values())), 1)
        )
        


        triangles = []
        while (len(triangles) < vertex_count - 3):
            # highlight current point
            schedule.append(
                (
                    drawing.create_alpha_color_blink_anim(0,0.8,0,
                        drawing.draw_triangle((
                            vertices.active.prev.value,
                            vertices.active.value,
                            vertices.active.next.value
                        ))
                    ), 2
                )
            )
            if self._is_ear(vertices):
                schedule.append(
                    (
                        drawing.create_alpha_color_anim(1,1,1, drawing.draw_polygon_vertex(vertices.active.value, 5), fill=True),
                        1
                    )
                )
                triangles.append(
                    (
                        vertices.active.prev.value,
                        vertices.active.value,
                        vertices.active.next.value
                    )
                )
                schedule.append((drawing.create_alpha_color_anim(1,1,1,drawing.draw_triangle(triangles[-1])), 1))
                vertices.remove()
            else:
                vertices.move_right()

        triangles.append(
            (
                vertices.active.prev.value,
                vertices.active.value,
                vertices.active.next.value
            )
        )
        schedule.append((drawing.create_alpha_color_anim(1,1,1,drawing.draw_triangle(triangles[-1])), 1))
        return schedule

    
    def _is_ear(self, vertices):
        v0 = vertices.active.prev.value
        v1 = vertices.active.value
        v2 = vertices.active.next.value
        
        if self._orientation(v0,v1,v2) > 0:
            return False

        curr = vertices.active.next.next
        for _ in range(len(vertices) - 3):
            if self._is_vertex_in_triangle(curr.value, v0, v1, v2):
                return False
            curr = curr.next
        return True

    def _is_vertex_in_triangle(self, v, v0, v1, v2):
        dx = v.x-v2.x
        dy = v.y-v2.y
        dx21 = v2.x-v1.x
        dy12 = v1.y-v2.y
        dx02 = v0.x - v2.x
        dy02 = v0.y - v2.y
        dy20 = v2.y-v0.y
        d = dy12*dx02 + dx21*dy02
        s = dy12*dx + dx21*dy
        t = dy20*dx + dx02*dy
        if d < 0:
            return s <= 0 and t <= 0 and s+t >= d
        else:
            return s <= 0 and t <= 0 and s+t <= d

    def _orientation(self, a, b, c):
        """Does c lie on, to the left of, or to the right of ab vector?"""
        return (a.x-c.x)*(b.y-c.y)-(b.x-c.x)*(a.y-c.y)
