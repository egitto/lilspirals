from math import e, pi, sin, cos, sqrt, log, sinh, cosh
from numpy import array, matrix
import time
from transforms3d import quaternions as quats

tau = 2*pi

def rPointFactory(z_of, r_of):
  # Factory for the rPoint class, just because I want to define the shape
  # functions z_of and r_of elsewhere
  class rPoint:
    def __init__(self, i, theta, t = 0):
      self.i = i
      self.r = r_of(t)
      self.theta = theta
      self.t = t
      self.x = cos(self.theta)*self.r
      self.y = sin(self.theta)*self.r
      self.z = z_of(t)
      self.char = str(int(self.z)%10)
    def xy_pos(self):
      return (self.x, self.y)
    def xyz_pos(self):
      return (self.x, self.y, self.z)
    def __repr__(self):
      return str((self.x,self.y,self.z))
  return rPoint

def makePoints(dTheta, n, rPoint, get_dt):
  old_z = old_r = 0
  # start t at 1, not 0, because otherwise the first get_dt
  t = 0 # units: "seconds" (not related to real time, all this is within one frame)
  old_dt = 1
  rPoints = []
  density = 3 # units: points per second
  for i in range(1,n):
    theta = (i * dTheta)
    point = rPoint(i, theta, t)
    rPoints += [point]
    z, r = point.z, point.r # z and radius given a particular time
    # dt = get_dt(density, r, r-old_r, z-old_z) # "wait" how long before making the next point?
    dt = get_dt(density, old_dt, r, r-old_r, z-old_z) # "wait" how long before making the next point?
    t += dt
    old_z, old_r, old_dt = z, r, dt
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

class overallShape:
  # just a helper class to hold the various shape functions
  def __init__(self):
    pass
  def r_of(self, t):
    # radius from center, given t where t increases monotonically with point number.
    return sin(t) + 1.01
    # return t**5
  def z_of(self, t):
    # depth from origin, given t where t increases monotonically with point number.
    return t / 200.0 - 10
  def get_dt(self, density, dt, r, dr, dz):
    # choose dt to achieve fixed dA of 1/density
    # assumption: dA is proportional to dt
    goal_dA = 1.0 / density # m^2 / point
    dA = r * sqrt(dz**2 + dr**2) # m^2
    dA = dA if dA else 1 # the first time, we won't have any data
    # square root is just for damping, don't want to over-adjust
    return dt * sqrt(goal_dA / dA)
  def get_dt_old(self, density, r, dr, dz):
    # amount to increment t by when progressing to the next point
    # t is kinda like time; it's a variable that increases. it's here to maintain even point density
    # unlike time, however, it has nothing to do with the animate function
    # dt units: s / points
    # t units: s (dt is ~integrated wrt points, which is multiplying, unit-wise)
    if r == 0:
      return 1
    dr = dr if dr else 1
    # unitless bit is related to arc length formula; I don't know why this works (I suspect it doesn't really)
    # 1 / ((points / m  / s) * m * (unitless)) = s / points
    return 1 / (density * r * sqrt(1 + (dz/dr)**2))

def animate(delay = .15, step = 0.00005, n = 380, size = (170,70), smooth = 4):
  i = 1
  q = (1, 0, 0, 0)
  shape = overallShape()
  rPoint = rPointFactory(shape.z_of, shape.r_of)
  while True:
    q = quats.qmult(q, quats.axangle2quat((0,1,0), .005*tau/smooth))
    # print(q)
    theta = tau/sqrt(2) + step*i/smooth
    ViewPoints(makePoints(theta, n, rPoint, shape.get_dt), size, rotateQuaternion = q).render()
    # print(theta)
    i += 1
    # n += 1
    time.sleep(delay/smooth)

# good values for theta: 2.33068600268, sqrt(2)*pi, sqrt(10)*pi, 2.32324311855, 4.62290939916, 20.7563962399, 2.32120903841

theta = sqrt(2)*pi
# ViewPoints(makePoints(theta, 300), size = (100,60), rotateQuaternion = (1,0.1,0,0)).render()
animate()