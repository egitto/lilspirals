from math import e, pi, sin, cos, sqrt, sinh, cosh
from numpy import array, matrix, dot, append, product
import time
from transforms3d import quaternions as quats
import sys

tau = 2*pi

def rPointFactory(z_of, r_of):
  # Factory for the rPoint class, just because I want to define the shape
  # functions z_of and r_of elsewhere
  class rPoint:
    def __init__(self, theta, t = 0):
      # Given floats t and theta, finds the proper r and z values,
      # and transforms those r and z values into xyz coordinates.
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

def makePoints(dTheta, n, shape):
  old_z = old_r = 0
  # start t at 1, not 0, because otherwise the first get_dt
  t = 0 # units: "seconds" (not related to real time, all this is within one frame)
  old_dt = 1
  rPoints = []
  density = n
  rPoint = rPointFactory(shape.z_of, shape.r_of)
  get_dt = shape.get_dt
  for i in range(1,n):
    theta = (i * dTheta)
    point = rPoint(theta, t)
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
      a[y][x] = max(a[y][x], str(pt[2]))
    printme = "".join(["\n" + "".join(row) for row in a])
    print(printme)

class overallShape:
  # just a helper class to hold the various shape functions
  def __init__(self, dA_i = 1, r_of = False, z_of = False, dMod = 1.0, name = 'unnamed', t_goal = False):
    # r_of is radius from center, given t where t increases monotonically with point number.
    # z_of is depth from origin, given t where t increases monotonically with point number.
    # dA_i is initial value of dA, for fine-tuning
    # dMod is (inverse) density mod, because some shapes work best with different densities.
    # higher dMod = less dense, so t will reach higher values
    self.r_of = r_of if r_of else lambda t: t
    self.z_of = z_of if z_of else lambda t: t
    self.dA_i = dA_i * 1.0
    self.dMod = dMod * 1.0
    self.t_goal = t_goal
    self.name = name
  def adjustDensity(self, points):
    if not self.t_goal: return
    ratio = (self.t_goal / points[-1].t)
    # overshot goal (big ratio)? decrease density (increase dMod)
    self.dMod *= sqrt(ratio)
  def get_dt(self, density, dt, r, dr, dz):
    # choose dt to achieve fixed dA of 1/density
    # assumption: dA is proportional to dt
    goal_dA = self.dMod / density # m^2 / point
    dA = r * sqrt(dz**2 + dr**2) # m^2 (technically we dropped a 2pi, but w/e)
    dA = dA if dA else self.dA_i # the first time, we won't have any data
    # square root is just for damping, don't want to over-adjust
    return dt * sqrt(goal_dA / dA)

def blendShapes(s1, s2, ratio = 0.5):
  # domain of s1, s2: overallShape x such that x.r_of(t) > 0 for all t > 0
  # domain of ratio: if x.z_of(t) > 0 for t > 0: any value besides 0 or 1
  #   otherwise, between 0 and 1
  def blendFxns(f1, f2):
    return lambda t: (f1(t) ** ratio) * (f2(t) ** (1 - ratio))
  def blendValues(a, b):
    return (a ** ratio) * (b ** (1 - ratio))
  r_of = blendFxns(s1.r_of, s2.r_of)
  z_of = blendFxns(s1.z_of, s2.z_of)
  dA_i = blendValues(s1.dA_i, s2.dA_i)
  dMod = blendValues(s1.dMod, s2.dMod)
  return overallShape(r_of = r_of, z_of = z_of, dA_i = dA_i, dMod = dMod)

class Rotation:
  def __init__(self, initialQuaternion = (1, 0, 0, 0), moveAngle = (1, 0, 0), speed = 0.005):
    self.moveAngle = moveAngle
    self.initialQuaternion = initialQuaternion
    self.speed = speed

def animate(shape, rotation, delay = .15, step = 0.00005, n = 400, size = (170,70), smooth = 4):
  i = 1
  q = rotation.initialQuaternion
  rotateBy = quats.axangle2quat(rotation.moveAngle, rotation.speed*tau/smooth)
  rPoint = rPointFactory(shape.z_of, shape.r_of)
  while True:
    q = quats.qmult(q, rotateBy)
    # print(q)
    theta = tau/sqrt(2) + step*i/smooth
    if shape.t_goal: shape.t_goal = i / 20.0
    points = makePoints(theta, n, shape)
    shape.adjustDensity(points)
    if (i != 1): sys.stdout.write("\033[F"*(size[1] + 1))
    ViewPoints(points, size, rotateQuaternion = q).render()
    # print(theta)
    i += 1
    # n += 1
    time.sleep(delay/smooth)

# pretty values for theta to be constant at: 2.33068600268, sqrt(2)*pi, sqrt(10)*pi, 2.32324311855, 4.62290939916, 20.7563962399, 2.32120903841

def identity(t):
  return t

def absinthe(t):
  return abs(sin(t))

cone = overallShape(r_of = identity, z_of = identity)
cylinder = overallShape(r_of = lambda t: 0.5, z_of = identity)
cappedCylinder = overallShape(r_of = lambda t: 0.5 if t >= 0.5 else t, z_of = lambda t: t if t >= 0.5 else 0.5)
pointyCone = overallShape(r_of = lambda t: t**2, z_of = lambda t: 10*t, dMod = 1000.0, dA_i = 10)
parabola = overallShape(r_of = identity, z_of = lambda t: t**2)

hemiSphere = overallShape(r_of = absinthe, z_of = cos, dMod = 1.0)
sphere = overallShape(r_of = absinthe, z_of = cos, dMod = 2.0)
smallSphere = overallShape(r_of = absinthe, z_of = cos, dMod = 4.0)
safeSphere = overallShape(r_of = absinthe, z_of = lambda t: cos(t) + 1.001, dMod = 2.0)

# torus = overallShape(r_of = lambda t: sin(t) + 2, z_of = cos, dMod = tau*2)
torus = overallShape(r_of = lambda t: sin(t) + 2, z_of = cos, t_goal = 0.01)

safeTorus = overallShape(r_of = lambda t: sin(t) + 2, z_of = lambda t: cos(t) + 1.001, dMod = tau*2)

ridges = overallShape(r_of = lambda t: sin(t) + 5, z_of = lambda t: t + 0.1, dMod = 100)

weirdThing1 = blendShapes(cone, safeSphere, ratio = 0.4)
weirdThing2 = blendShapes(safeTorus, cappedCylinder, ratio = 0.4)

offAxis = Rotation(initialQuaternion = (0, 1, 0, 0), moveAngle = (0, 1, 0), speed = 0.05)
christmasTree = Rotation(initialQuaternion = (2**-0.5, 2**-0.5, 0, 0), speed = 0)
spinningTree = Rotation(initialQuaternion = (2**-0.5, 2**-0.5, 0, 0), moveAngle = (0, 1, 0))
headOnSpin = Rotation(initialQuaternion = (0, 0, 0, 1), moveAngle = (0, 0, 1), speed = 0.001)
noRotation = Rotation(initialQuaternion = (0, 0, 0, 1), speed = 0)

# import cProfile
# cProfile.run('animate(shape = torus, rotation = offAxis, n = 400)')

animate(shape = torus, rotation = offAxis, n = 400)
