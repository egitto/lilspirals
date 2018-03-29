from math import e, pi, sin, cos, sqrt, log
from numpy import array, matrix
import time
from transforms3d import quaternions as quats

e = e
theta = 2*pi/e
tau = 2*pi

class spiralPoint:
  def __init__(self, n, theta = 2*pi/e):
    self.n = n
    self.theta = theta
    self.char = str(n%2)
    self.x = self.r()*cos(theta)
    self.y = self.r()*sin(theta)
    self.z = 0
  def r(self):
    return self.theta*(self.n**0.5)
  def xy_pos(self):
    return (self.x, self.y)
  def xyz_pos(self):
    return (self.x, self.y, self.z)

def getPoints(theta, n):
    return [spiralPoint(i, theta) for i in range(n)]

class rPoint:
  def __init__(self, i, theta, w = 0):
    self.i = i
    self.r = self.r_of(w)
    self.theta = theta 
    self.w = w
    self.x = cos(self.theta)*self.r
    self.y = sin(self.theta)*self.r
    self.z = self.z_of(w)
    self.char = str(int(self.z/5)%10)
  def xy_pos(self):
    return (self.x, self.y)
  def xyz_pos(self):
    return (self.x, self.y, self.z)
  def r_of(self, w):
    return w
  def z_of(self, w):
    return w**1.2
  def __repr__(self):
    return str((self.x,self.y,self.z))


def get_dA(r, dr, dz):
  return tau * r * get_dS(dr, dz)

def get_dS(dr, dz):
  if dr == 0:
    return 1
  return (1 + (dz/dr)**2)**0.5

def makePoints(dTheta, n):
  old_z = old_r = 0
  w = 1
  A = 0
  s = 0
  tau = 2*pi
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
    self.xyz_points = self.get_xyz_points(points, rotateQuaternion)
    self.size = size
  def get_xyz_points(self, points, rotateQuaternion):
    rotateMatrix = matrix(quats.quat2mat(rotateQuaternion))
    return {
      pt: array(matrix(pt.xyz_pos())*rotateMatrix)
      for pt in points
    }
  def autoscale(self):
    m = max([max(map(abs,pt.xy_pos())) for pt in self.points])
    return [(self.size[i]/m/2.0) for i in range(len(self.size))]
  def scale(self, xy_pos, zoom): # this should be in spiralPoint
    return tuple([xy_pos[i]*zoom[i] for i in range(len(xy_pos))])
  def translate(self, xy_pos, shift): # this should be in spiralPoint
    return tuple([xy_pos[i]+shift[i] for i in range(len(xy_pos))])
  def pr(self):
    dx, dy = self.size
    a = array([[' ']*dx]*dy)
    zoom = self.autoscale()
    a[dy//2][dx//2] = 'x'
    for pt in self.points:
      x,z,y = self.xyz_points[pt][0]
      x,y = self.scale((x,y), zoom)
      x,y = self.translate((x,y), (dx/2, dy/2))
      a[int(y)%dy][int(x)%dx] = pt.char
    printme = ""
    for row in a:
      s = "\n"
      for chr in row:
        s += chr
      printme += s
    print(printme)

def animate(delay = .1, step = 0.00002, n = 900, size = (100,60)):
  i = 1
  q = (1, 0, 0, 0)
  while True:
    q = quats.qmult(q, (1, 0.01, 0, 0))
    theta = pi*sqrt(2) + step*i
    ViewPoints(makePoints(theta, n), size, rotateQuaternion = q).pr()
    print(theta)
    i += 1
    time.sleep(delay)

# good values for theta: 2.33068600268, sqrt(2)*pi, sqrt(10)*pi, 2.32324311855, 4.62290939916, 20.7563962399, 2.32120903841

theta = sqrt(2)*pi
# ViewPoints(makePoints(theta, 300), size = (100,60), rotateQuaternion = (1,0.1,0,0)).pr()
animate()