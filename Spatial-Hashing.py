# class Spatialhash:
#     def __init__(self, cell_size) -> None:
#         self.cell_size = cell_size
#         self.contents = {}
    
#     def hashPoint(self,point: Point):
#         return int(point.x/self.cell_size), int(point.x/self.cell_size)

#     def insert(self,point: Point):
#         self.contents.setdefault( self.hashPoint(point), [] ).append(point.idx)
    
# class SpatialHashGrid:
#     def __init__(self, bounds, dimensions) -> None:
#         self.bounds = bounds
#         self.dimensions = dimensions
#         self.cells = {

#         }

#     def newclient(self, position, dimensions):
#         client = {
#             position : position,
#             dimensions : dimensions,
#             indices : None
#         }
#         self.insert(client)

#         return client

#     def insert(self, client):
#         x, y = client.position
#         w, h = client.dimensions

#         i1 = self.getcellindex([x-w/2, y-h/2])
#         i2 = self.getcellindex([x+w/2, y+h/2])

#         client.indices = [i1, i2]

#         for i in range(i1[0], i2[0]+1, 1):
#             for j in range(i1[1], i2[1]+1, 1):
#                 k = self.key(i, j)
#                 if not k in self.cells.keys():
#                     self.cells[k] = {}
#                 self.cells[k].add(client)

#     def key(self, i, j):
#         return i+'.'+j

#     def getcellindex(self, position):
#         x = (position[0]-self.bounds[0])/(self.bounds)

#     def findnear(self, position, bounds):
#         x, y = position
#         w, h = bounds

#         i1 = self.getcellindex([x-w/2, y-h/2])
#         i2 = self.getcellindex([x+w/2, y+h/2])

#         clients = {}

#         for i in range(i1[0], i2[0]+1, 1):
#             for j in range(i1[1], i2[1]+1, 1):
#                 k = self.key(i, j)
#                 if not k in self.cells.keys():
#                     for l in self.cells[k]:
#                         clients.add(l)

#     def updateclient(self, client):
#         self.removeclient(client)
#         self.insert(client)

#     def removeclient(self, client):
#         i1, i2 = client.indices

#         for i in range(i1[0], i2[0]+1, 1):
#             for j in range(i1[1], i2[1]+1, 1):
#                 k = self.key(i, j)

#                 self.cells[k].remove(client)


# grid = SpatialHashGrid(bounds, dimensions)

# client = grid.newclient(parameters)
# client.position = newposition
# grid.updateclient(client)

# nearby = grid.findnear(location, bounds)

# grid.removeclient(client)

class Point:
    def __init__(self, x: float = 0, y: float = 0, idx: int = 0) -> None:
        self.x = x
        self.y = y
        self.idx = idx

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
            if self.hash.has_key(key):
                found.extend(self.hash[key])
        
        if point.idx in found:
            found.remove(point.idx)
        return found