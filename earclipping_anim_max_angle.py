import math
import point

import drawing
from linkedlist import DoublyLinkedList


class EarClippingAnimMaxAngle:
    def __init__(self, vertices):
        # order vertices to be counter-clockwise
        if not self._is_clockwise(vertices):
            vertices = list(reversed(vertices))

        # build the animation schedule
        self.schedule = self._build_schedule(vertices)
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
        limit = 10000
        counter = 0
        while (len(triangles) < vertex_count - 3):
            ears = []
            for offset in range(len(vertices)):

                # highlight current point
                conflicts = self._get_conflicting(vertices)
                conflicts_anims = []
                for conflict in conflicts:
                    conflicts_anims.append(
                        drawing.create_polygon_vertex_blink_anim(
                            conflict, vertex_radius, (1,0,0)
                        )
                    )

                conflicts_anims.append(drawing.create_polygon_vertex_blink_anim(vertices.active.value, 1.5*vertex_radius, (0,1,0)))
                conflicts_anims.append(
                    drawing.create_alpha_color_blink_anim(0,0.8,0,
                        drawing.draw_triangle((
                            vertices.active.prev.value,
                            vertices.active.value,
                            vertices.active.next.value
                        ))
                    )
                )
                schedule.append((drawing.parallel_anims(conflicts_anims), 2))

                if self._is_ear(vertices):
                    ears.append((offset, vertices.active))
                
                vertices.move_right()
            
            max_ear_offset, max_ear = max(ears, key=lambda a: self._min_angle(a[1].prev.value, a[1].value, a[1].next.value))
            schedule.append(
                (
                    drawing.create_alpha_color_anim(1,1,1, drawing.draw_polygon_vertex(max_ear.value, vertex_radius), fill=True),
                    1
                )
            )
            triangles.append(
                (
                    max_ear.prev.value,
                    max_ear.value,
                    max_ear.next.value
                )
            )
            schedule.append((drawing.create_alpha_color_anim(1,1,1,drawing.draw_triangle(triangles[-1])), 1))

            for _ in range(max_ear_offset):
                vertices.move_right()
            vertices.remove()


            counter += 1
            if counter >= limit:
                break

        schedule.append(
            (
                drawing.create_alpha_color_anim(1,1,1, drawing.draw_polygon_vertex(vertices.active.prev.value, vertex_radius), fill=True),
                1
            )
        )
        schedule.append(
            (
                drawing.create_alpha_color_anim(1,1,1, drawing.draw_polygon_vertex(vertices.active.value, vertex_radius), fill=True),
                1
            )
        )
        schedule.append(
            (
                drawing.create_alpha_color_anim(1,1,1, drawing.draw_polygon_vertex(vertices.active.next.value, vertex_radius), fill=True),
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

    def _get_conflicting(self, vertices):
        v0 = vertices.active.prev.value
        v1 = vertices.active.value
        v2 = vertices.active.next.value
        
        conflicts = []

        if self._orientation(v0,v1,v2) > 0:
            return conflicts

        curr = vertices.active.next.next
        for _ in range(len(vertices) - 3):
            if self._is_vertex_in_triangle(curr.value, v0, v1, v2):
                conflicts.append(curr.value)
            curr = curr.next
        return conflicts

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
    
    def _is_clockwise(self, vertices):
        """Determins whether a polygon is clockwise or anti-clockwise"""
        criterion = 0
        vertex_count = len(vertices)
        for i in range(0, vertex_count ):
            a = i
            b = (i + 1) % vertex_count
            criterion += (vertices[b].x - vertices[a].x)*(vertices[b].y + vertices[a].y)

        return criterion > 0
    
    def _min_angle(self, a, b, c):
        """Returns minimum angle in a triangle defined by 3 vertices"""
        v_ab = point.point_diff(b, a)
        v_ac = point.point_diff(c, a)
        v_bc = point.point_diff(c, b)
        
        alpha = math.acos(point.point_scalar(v_ac, v_ab))
        gamma = math.acos(point.point_scalar(v_ac, v_bc))
        beta = math.pi - alpha - gamma
        return min(alpha, beta, gamma)