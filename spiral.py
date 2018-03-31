from math import e, pi, sin, cos, sqrt, log, sinh, cosh
from numpy import array, matrix
import time
from transforms3d import quaternions as quats

tau = 2*pi

class rPoint:
  def __init__(self, i, theta, w = 0):
    self.i = i
    self.r = self.r_of(w)
    self.theta = theta 
    self.w = w
    self.x = cos(self.theta)*self.r
    self.y = sin(self.theta)*self.r
    self.z = self.z_of(w)
    self.char = str(int(self.z)%10)
  def xy_pos(self):
    return (self.x, self.y)
  def xyz_pos(self):
    return (self.x, self.y, self.z)
  def r_of(self, w):
    return w**5
  def z_of(self, w):
    return w*100-200
  def __repr__(self):
    return str((self.x,self.y,self.z))

def get_dS(dr, dz):
  # arc length formula; I'm confused as to why it works, though
  if dr == 0:
    return 1
  return (1 + (dz/dr)**2)**0.5

def makePoints(dTheta, n):
  old_z = old_r = 0
  w = 1
  A = 0
  s = 0
  rPoints = []
  density = 3
  for i in range(1,n):
    theta = (i * dTheta)
    point = rPoint(i, theta, w)
    rPoints += [point]
    z, r = point.z, point.r
    w += 1 / (density * r * get_dS(r-old_r, z-old_z))
    old_z, old_r = z, r
  return rPoints

class ViewPoints:
  def __init__(self, points, size = (240,100), rotateQuaternion = (1,0,0,0)):
    self.points = points
    self.xyz_points = self.get_xyz_points(points, rotateQuaternion) # dictionary
    self.size = size
  def get_xyz_points(self, points, rotateQuaternion):
    rotateMatrix = matrix(quats.quat2mat(rotateQuaternion))
    return {
      pt: array(matrix(pt.xyz_pos())*rotateMatrix)[0]
      for pt in points
    }
  def render(self):
    points = array([[
        self.xyz_points[pt][0], 
        self.xyz_points[pt][1],
        int(self.xyz_points[pt][2])]
        for pt in self.points])
    RenderXY(points, size = self.size).pr()

# prevents jitter
class Bounds:
  def __init__(self):
    self.Xmin = self.Ymin = 10**100
    self.Ymax = self.Xmax = -(10**100)

class RenderXY:
  def __init__(self, points, size = (240, 100), persistentBounds = Bounds()):
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
      a[y][x] = pt[2]
    printme = ""
    for row in a:
      s = "\n"
      for ch in row:
        s += str(ch)
      printme += s
    print(printme)

def animate(delay = .15, step = 0.0005, n = 380, size = (170,70), smooth = 4):
  i = 1
  q = (1, 0, 0, 0)
  while True:
    q = quats.qmult(q, quats.axangle2quat((0,1,0), .005*tau/smooth))
    print(q)
    theta = tau/sqrt(2) + step*i/smooth
    ViewPoints(makePoints(theta, n), size, rotateQuaternion = q).render()
    print(theta)
    i += 1
    time.sleep(delay/smooth)

# good values for theta: 2.33068600268, sqrt(2)*pi, sqrt(10)*pi, 2.32324311855, 4.62290939916, 20.7563962399, 2.32120903841

theta = sqrt(2)*pi
# ViewPoints(makePoints(theta, 300), size = (100,60), rotateQuaternion = (1,0.1,0,0)).render()
animate()