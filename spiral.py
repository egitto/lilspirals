from math import e, pi, sin, cos, sqrt, log
from numpy import array
import time

e = e
theta = 2*pi/e
tau = 2*pi

class spiralPoint:
  def __init__(self, n, theta = 2*pi/e):
    self.n = n
    self.theta = theta
    self.char = str(n%2)
  def r(self):
    return self.theta*(self.n**0.5)
  def pos(self):
    r = self.r()
    th = self.theta * self.n
    return array((r*cos(th), r*sin(th)))

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
    self.char = str(int(log(self.z))%10)
  def pos(self):
    return (self.x, self.y)
  def r_of(self, w):
    return w
  def z_of(self, w):
    return w
  def __repr__(self):
    return str((self.x,self.y))


def get_dA(r, dr, dz):
  return tau * r * get_dS(dr, dz)

def get_dS(dr, dz):
  return (dr**2 + dz**2)**0.5

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
    dA = get_dA(r, r-old_r, z-old_z)
    A += dA
    # w += 1/(density * dA(r, r-old_r, z-old_z))
    w = i / A
    old_z, old_r = z, r
  return rPoints

class ViewPoints:
  def __init__(self, points, size = (240,100)):
    self.points = points
    self.size = size
  def autoscale(self):
    m = max([max(map(abs,pt.pos())) for pt in self.points])
    return [(self.size[i]/m/2.0) for i in range(len(self.size))]
  def scale(self, pos, zoom): # this should be in spiralPoint
    return tuple([pos[i]*zoom[i] for i in range(len(pos))])
  def translate(self, pos, shift): # this should be in spiralPoint
    return tuple([pos[i]+shift[i] for i in range(len(pos))])
  def pr(self):
    dx, dy = self.size
    a = array([[' ']*dx]*dy)
    a[dy//2][dx//2] = 'x'
    zoom = self.autoscale()
    for pt in self.points:
      x,y = pt.pos()
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


def animate(delay = 0.2, step = 0.0000002, n = 900, size = (300,100)):
  i = 1
  while True:
    ViewPoints(makePoints(theta*(1+step*i), n), size).pr()
    print(theta*(1+step*i))
    i += 100
    time.sleep(delay)

# good values for theta: 2.33068600268, sqrt(2)*pi, sqrt(10)*pi, 2.32324311855, 4.62290939916, 20.7563962399, 2.32120903841

theta = sqrt(2)*pi
# ViewPoints(makePoints(theta, 300), size = (100,60)).pr()
animate()