from Point import Point

class SpatialHash:
    def __init__(self,screen_width: float = 1200.0, screen_height: float = 700.0 ,radius: float = 0) -> None:
        self.screen_height = screen_height
        self.screen_width =screen_width
        self.radius = radius
        self.hash = {}
    
    def hashPoint(self, point: Point):
        xidx = int(point.x/self.radius)
        yidx = int(point.y/self.radius)
        return xidx,yidx

    def insertPoint(self, point: Point) ->None:
        self.hash.setdefault( self.hashPoint(point), [] ).append(point.idx)

    def queryPoint(self, point: Point):
        found = []
        xidx = int(point.x/self.radius)
        yidx = int(point.y/self.radius)

        keys = [(xidx,yidx),(xidx+1,yidx+1),(xidx-1,yidx-1),(xidx-1,yidx+1),
                (xidx+1,yidx-1),(xidx,yidx+1),(xidx,yidx-1),(xidx+1,yidx),(xidx-1,yidx)]

        for key in keys:
            if key in self.hash:
                found.extend(self.hash[key])
        
        if point.idx in found:
            found.remove(point.idx)
        return found