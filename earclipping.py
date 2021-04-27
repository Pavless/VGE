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

def ear_clipping(points):
    # init
    point_count = len(points)
    
    point_iter = iter(points)
    first = next(point_iter)
    vertices = DoublyLinkedList(first)
    for point in point_iter:
        vertices.insert_end(point)

    triangles = []

    while (len(triangles) < point_count - 3):
        if is_ear(vertices):
            triangles.append(
                (
                    vertices.active.prev.value,
                    vertices.active.value,
                    vertices.active.next.value
                )
            )
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

    return triangles
    
def is_ear(vertices):
    v0 = vertices.active.prev.value
    v1 = vertices.active.value
    v2 = vertices.active.next.value
    
    if orientation(v0,v1,v2) > 0:
        return False

    curr = vertices.active.next.next
    for _ in range(len(vertices) - 3):
        if is_vertex_in_triangle(curr.value, v0, v1, v2):
            return False
        curr = curr.next
    return True

def is_vertex_in_triangle(v, v0, v1, v2):
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

def find_intersection(x1,y1,x2,y2,x3,y3,x4,y4):
  try:
      uA = ((x4-x3)*(y1-y3) - (y4-y3)*(x1-x3)) / ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1));
      uB = ((x2-x1)*(y1-y3) - (y2-y1)*(x1-x3)) / ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1));
  except:
      return None
  if (uA >= 0 and uA <= 1 and uB >= 0 and uB <= 1):
      intersectionX = x1 + (uA * (x2-x1));
      intersectionY = y1 + (uA * (y2-y1));
      return point.Point(intersectionX, intersectionY)
  return None

def check_intersections(polygon):
    poly = polygon[:]
    poly.append(polygon[0])
    tmp = poly[:]
    intersections = []
    for l1, l2 in zip(poly, poly[1:]):
        tmp = tmp[1:]
        for n1,n2 in zip(tmp,tmp[1:]):
            ret = find_intersection(l1[0],l1[1],l2[0],l2[1],n1[0],n1[1],n2[0],n2[1])
            if ret and (ret != l2) and (ret != l1):
                intersections.append(ret)
    return intersections

def collinear(x1, y1, x2, y2, x3, y3): 
    a = x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)
    return (a==0)

def check_points_on_line(polygon):
    pts = []
    poly = polygon[:]
    poly.append(polygon[0])
    for p1, p2, p3 in zip(poly, poly[1:], poly[2:]):
        if(collinear(p1[0],p1[1],p2[0],p2[1],p3[0],p3[1])):
            pts.append(p2)    
    out = []
    for p in polygon:
        if p not in pts:
            out.append(p)
            
    return out,pts
    

def orientation(a, b, c):
    """Does c lie on, to the left of, or to the right of ab vector?"""
    return (a.x-c.x)*(b.y-c.y)-(b.x-c.x)*(a.y-c.y)

def rotate_list(l, shift):
    n = []
    for i in range(shift, len(l)):
        n.append(l[i])
    for i in range(0, shift):
        n.append(l[i])
    return n

def main():
    points = [
        point.Point(1,1),
        point.Point(1,-1),
        point.Point(0,0),
        point.Point(-1,-1),
        point.Point(-1,1),
        point.Point(0, 2)
    ]
    for shift in range(len(points)):
        tmp = rotate_list(points, shift)
        triangles = ear_clipping(tmp)
        print(triangles)
        print()

if __name__ == "__main__":
    main()