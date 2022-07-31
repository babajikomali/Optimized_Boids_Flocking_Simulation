from Point import Point

class Circle:
    def __init__(self, x: float = 0, y: float = 0, r: float = 0, idx: int = 0) -> None:
        self.x = x
        self.y = y
        self.r = r
        self.idx = idx

    def isContain(self, point: Point) -> bool:
        diff_x = abs(point.x - self.x)
        diff_y = abs(point.y - self.y)

        if diff_x > self.r:
            return False
        if diff_y > self.r:
            return False
        if diff_x + diff_y <= self.r:
            return True
        if diff_x**2 + diff_y**2 <= self.r**2:
            return True

        return False
