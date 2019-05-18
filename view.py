from transforms3d import quaternions as quats
from numpy import matrix, array, dot

class ViewPoints:
  def __init__(self, points, size = (240,100), rotateQuaternion = (1,0,0,0)):
    self.points = points
    self.rotated_points = self.get_rotated_points(rotateQuaternion)
    self.size = size
  def get_rotated_points(self, rotateQuaternion):
    rotateMatrix = matrix(quats.quat2mat(rotateQuaternion))
    xyz = array([pt.xyz_pos() for pt in self.points])
    return array(dot(xyz, rotateMatrix))
  def render(self):
    RenderXY(self.rotated_points, size = self.size).pr()

# prevents jitter
class Bounds:
  def __init__(self):
    self.Xmin = self.Ymin = 10**100
    self.Ymax = self.Xmax = -(10**100)

# _technically_ I could just say "persistentBounds = Bounds()" but this is clearer
boundsSingleton = Bounds()

class RenderXY:
  def __init__(self, points, size = (240, 100), persistentBounds = boundsSingleton):
    self.x, self.y = size
    self.persistentBounds = persistentBounds
    self.scaled_points = self.scale(points)
  def scale(self, points_XYetc):
    xs = points_XYetc[:,0]
    ys = points_XYetc[:,1]
    ch = points_XYetc[:,2]
    s = self.persistentBounds # alias for conciseness
    s.Xmin, s.Ymin = min(xs.min(), s.Xmin), min(ys.min(), s.Ymin)
    s.Xmax, s.Ymax = max(xs.max(), s.Xmax), max(ys.max(), s.Ymax)
    xs = (xs - s.Xmin) * (self.x - 1) / (s.Xmax - s.Xmin)
    ys = (ys - s.Ymin) * (self.y - 1) / (s.Ymax - s.Ymin)
    return zip(xs, ys, ch)
  def pr(self):
    a = array([[' ']*self.x]*self.y)
    for pt in self.scaled_points:
      y = int(pt[1])%self.y
      x = int(pt[0])%self.x
      a[y][x] = max(a[y][x], str(pt[2]))
    printme = "".join(["\n" + "".join(row) for row in a])
    print(printme)