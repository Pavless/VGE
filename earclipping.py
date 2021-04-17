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