import math

from sortedcontainers import SortedDict
import drawing
import point
from linkedlist import DoublyLinkedList, DoublyLinkedItem

EPS=1e-7

class EarClippingAnim:
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

    def _build_schedule(self, vertices_list):
        """Build a animation schedule by walking the steps of the algorithm"""
        if len(vertices_list) < 3:
            raise ValueError("vertices should have at least 3 items")
        
        ear_color = (0,.7,0)
        non_ear_color = (.7,0,0)
        vertex_radius = 5
        schedule = []

        # initialize linked list containing vertices
        vertex_iter = iter(vertices_list)
        vertices = DoublyLinkedList(next(vertex_iter))
        for vertex in vertex_iter:
            vertices.insert_end(vertex)

        # draw outline of the polygon
        schedule.append(
            (drawing.create_alpha_color_anim(0.26, 0.65, 0.77, drawing.draw_polygon_segments(vertices.enumerate_values())), 1)
        )

        # create a sorted dict of ears
        ears = SortedDict() # key is the max-min angle value is the linked list item
        from_vertex_to_ear_key = dict() # backwards links to items in ears
        for _ in range(len(vertices)):
            # highlight current point
            conflicts = self._get_conflicting(vertices.active.prev, vertices.active, vertices.active.next, vertices_list)
            conflicts_anims = []
            for conflict in conflicts:
                conflicts_anims.append(drawing.create_polygon_vertex_blink_anim(conflict, vertex_radius, (1,0,0)))

            conflicts_anims.append(drawing.create_polygon_vertex_blink_anim(vertices.active.value, 1.5*vertex_radius, (0,1,0)))
            conflicts_anims.append(drawing.create_alpha_color_blink_anim(0,0.8,0, drawing.draw_triangle((vertices.active.prev.value, vertices.active.value, vertices.active.next.value))))
            schedule.append((drawing.parallel_anims(conflicts_anims), 2))

            if self._is_ear(vertices.active.prev, vertices.active, vertices.active.next, vertices_list):
                # mark as ear
                #schedule.append((drawing.create_alpha_color_anim(*ear_color, drawing.draw_polygon_vertex(vertices.active.value, vertex_radius), True), 1))

                minmax_angle = self._min_angle(vertices.active.prev.value, vertices.active.value, vertices.active.next.value)
                while minmax_angle in ears: # break equality
                    minmax_angle += EPS
                ears[minmax_angle] = vertices.active
                from_vertex_to_ear_key[vertices.active.value] = minmax_angle
            else:
                # mark as non-ear
                from_vertex_to_ear_key[vertices.active.value] = vertices.active
                #schedule.append((drawing.create_alpha_color_anim(*non_ear_color, drawing.draw_polygon_vertex(vertices.active.value, vertex_radius), True), 1))
            vertices.move_right()

        triangles = []
        while len(vertices) > 2:
            _, selected_ear = ears.popitem()
            schedule.append((drawing.create_pause_anim(), 1))
            schedule.append((drawing.create_alpha_color_blink_anim(1,1,1, drawing.draw_triangle((selected_ear.prev.value, selected_ear.value, selected_ear.next.value))),2))
            schedule.append((drawing.create_alpha_color_anim(1,1,1, drawing.draw_polygon_vertex(selected_ear.prev.value, vertex_radius), fill=True),0.5))
            schedule.append((drawing.create_alpha_color_anim(1,1,1, drawing.draw_polygon_vertex(selected_ear.value, vertex_radius), fill=True),0.5))
            schedule.append((drawing.create_alpha_color_anim(1,1,1, drawing.draw_polygon_vertex(selected_ear.next.value, vertex_radius), fill=True),0.5))
            triangles.append((selected_ear.prev.value, selected_ear.value, selected_ear.next.value))
            schedule.append((drawing.create_alpha_color_anim(1,1,1,drawing.draw_triangle(triangles[-1])), 1))
            # update neighbours
            neigbours_keys = [selected_ear.prev.value, selected_ear.next.value]
            vertices.remove_item(selected_ear)
            if len(vertices) > 3:
                for neighbour_key in neigbours_keys:
                    item = from_vertex_to_ear_key[neighbour_key]
                    if isinstance(item, float):
                        item = ears.pop(item)

                    # highlight current point
                    conflicts = self._get_conflicting(item.prev, item, item.next, vertices_list)
                    conflicts_anims = []
                    for conflict in conflicts:
                        conflicts_anims.append(drawing.create_polygon_vertex_blink_anim(conflict, vertex_radius, (1,0,0)))

                    conflicts_anims.append(drawing.create_polygon_vertex_blink_anim(item.value, 1.5*vertex_radius, (0,1,0)))
                    conflicts_anims.append(drawing.create_alpha_color_blink_anim(0,0.8,0, drawing.draw_triangle((item.prev.value, item.value, item.next.value))))
                    schedule.append((drawing.parallel_anims(conflicts_anims), 2))

                    if self._is_ear(item.prev, item, item.next, vertices_list):
                        # mark as ear
                        #schedule.append((drawing.create_alpha_color_anim(*ear_color, drawing.draw_polygon_vertex(item.value, vertex_radius), True), 1))

                        minmax_angle = self._min_angle(item.prev.value, item.value, item.next.value)
                        while minmax_angle in ears: # break equality
                            minmax_angle += EPS
                        ears[minmax_angle] = item
                        from_vertex_to_ear_key[item.value] = minmax_angle
                    else:
                        # mark as non-ear
                        #schedule.append((drawing.create_alpha_color_anim(*non_ear_color, drawing.draw_polygon_vertex(item.value, vertex_radius), True), 1))
                        from_vertex_to_ear_key[item.value] = item
        
        # fill the polygon
        schedule.append(
            (drawing.create_alpha_color_anim(1, 1, 1, drawing.draw_polygon_segments(vertices_list), True, 0.3), 1)
        )

        return schedule

    
    def _is_ear(self, i0, i1, i2, all_vertices):
        if self._orientation(i0.value,i1.value,i2.value) > 0:
            return False
        return len(self._get_conflicting(i0, i1, i2, all_vertices)) == 0

    def _get_conflicting(self, i0, i1, i2, all_vertices):
        v0 = i0.value
        v1 = i1.value
        v2 = i2.value

        conflicts = []

        if self._orientation(v0,v1,v2) > 0:
            return conflicts

        for vertex in all_vertices:
            if not point.point_eq(vertex, v0) and not point.point_eq(vertex, v1) and not point.point_eq(vertex, v2) and self._is_vertex_in_triangle(vertex, v0, v1, v2):
                conflicts.append(vertex)
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