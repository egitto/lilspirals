#!python
from math import e, pi, sin, cos, sqrt, sinh, cosh
from numpy import array, matrix, dot, append, product, log, exp
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
  t = shape.t_i # units: "seconds" (not related to real time, all this is within one frame)
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
  def __init__(self, dA_i = 1, r_of = False, z_of = False, dMod = 1, name = 'unnamed', t_f = 0, t_i = 0, max_dt = 9E99):
    # r_of is radius from center, given t where t increases monotonically with point number.
    # z_of is depth from origin, given t where t increases monotonically with point number.
    # dA_i is initial value of dA, for fine-tuning
    # dMod is (inverse) density mut, because some shapes work best with different densities.
    # higher dMod = less dense, so t will reach higher values
    self.r_of = r_of if r_of else lambda t: t
    self.z_of = z_of if z_of else lambda t: t
    self.dA_i = dA_i * 1.0
    self.dMod = dMod * 1.0
    self.t_f = t_f * 1.0
    self.t_i = t_i * 1.0
    self.max_dt = max_dt * 1.0
    self.name = name
  def adjustDensity(self, points):
    if not self.t_f: return
    ratio = (self.t_f / points[-1].t)
    # overshot goal (big ratio)? decrease density (increase dMod)
    self.dMod *= sqrt(ratio) # sqrt to prevent oscillations
  def get_dt(self, density, dt, r, dr, dz):
    # choose dt to achieve fixed dA of 1/density
    # assumption: dA is proportional to dt
    goal_dA = self.dMod / density # m^2 / point
    dA = r * sqrt(dz**2 + dr**2) # m^2 (technically we dropped a 2pi, but w/e)
    dA = dA if dA else self.dA_i # the first time, we won't have any data
    # square root is just for damping, don't want to over-adjust
    goal_dt = dt * sqrt(goal_dA / dA)
    return min(self.max_dt, goal_dt)

def geoBlend(s1, s2, ratio = 0.5, **kwargs):
  # domain of s1, s2: overallShape x such that x.r_of(t) > 0 for all t > 0
  # domain of ratio: if x.z_of(t) > 0 for t > 0: any value besides 0 or 1
  #   otherwise, between 0 and 1
  def blendFxns(f1, f2):
    return lambda t: (f1(t) ** ratio) * (f2(t) ** (1 - ratio))
  r_of = blendFxns(s1.r_of, s2.r_of)
  z_of = blendFxns(s1.z_of, s2.z_of)
  return overallShape(r_of = r_of, z_of = z_of, **kwargs)

def arithBlend(s1, s2, ratio = 0.5, **kwargs):
  # domain of s1, s2: overallShape x such that x.r_of(t) > 0 for all t > 0
  # domain of ratio: if x.z_of(t) > 0 for t > 0: any value besides 0 or 1
  #   otherwise, between 0 and 1
  def blendFxns(f1, f2):
    return lambda t: (f1(t) * ratio) + (f2(t) * (1 - ratio))
  r_of = blendFxns(s1.r_of, s2.r_of)
  z_of = blendFxns(s1.z_of, s2.z_of)
  return overallShape(r_of = r_of, z_of = z_of, **kwargs)

class Rotation:
  def __init__(self, initialQuaternion = (1, 0, 0, 0), moveAngle = (1, 0, 0), speed = 0.005):
    self.moveAngle = moveAngle
    self.initialQuaternion = initialQuaternion
    self.speed = speed

class Texture:
  def __init__(self, theta):
    self.theta = theta

def animate(shape, rotation, mutators = [], delay = .15, step = 0.00005, n = 400, size = (170,70), smooth = 4.):
  i = 1
  q = rotation.initialQuaternion
  rotateBy = quats.axangle2quat(rotation.moveAngle, rotation.speed*tau/smooth)
  texture = Texture(theta = tau/sqrt(2))
  while True:
    q = quats.qmult(q, rotateBy)
    # print(q)
    [mut(shape = shape, i = i/smooth, texture = texture) for mut in mutators]
    points = makePoints(texture.theta, n, shape)
    if (i != 1): sys.stdout.write("\033[F"*(size[1] + 1))
    shape.adjustDensity(points)
    ViewPoints(points, size, rotateQuaternion = q).render()
    # print(theta)
    i += 1
    time.sleep(delay/smooth)


class mutators:
  def __init__(self):
    pass
  def deltaTheta(self, dTheta):
    def fxn(texture, **kwargs):
      texture.theta += dTheta
    return fxn
  def fixedTheta(self, theta):
    def fxn(texture, **kwargs):
      texture.theta = theta
    return fxn
  def oscillatingTheta(self, theta, amp, freq):
    def fxn(texture, i, **kwargs):
      texture.theta = theta + tau * amp * sin(i * freq)
    return fxn
  def expandShape(self, rate):
    # when t_f is too big, errors in dt calculation accumulate, which can make it flip out
    # you may want to set a max_dt if that happens, or use oscillateShape instead
    def fxn(shape, **kwargs):
      shape.t_f += rate
    return fxn
  def oscillateShape(self, center, amp, freq):
    def fxn(shape, i, **kwargs):
      shape.t_f = center + amp * sin(i * freq)
    return fxn
  def oscillate_t_i(self, center, amp, freq):
    def fxn(shape, i, **kwargs):
      shape.t_i = center + amp * sin(i * freq)
    return fxn
  def adjust_dA_i(self, shape, **kwargs):
    shape.dA_i += 0.1
  def force_dt(self, shape, **kwargs):
    shape.max_dt += 0.05

# pretty values for theta to be constant at: 2.33068600268, sqrt(2)*pi, sqrt(10)*pi, 2.32324311855, 4.62290939916, 20.7563962399, 2.32120903841

def identity(t):
  return t

def absinthe(t):
  return abs(sin(t))

# Example basic shapes
plane = overallShape(r_of = identity, z_of = lambda t: 0)
cone = overallShape(r_of = identity, z_of = identity)
cylinder = overallShape(r_of = lambda t: 0.5, z_of = identity)
cappedCylinder = overallShape(r_of = lambda t: 0.5 if t >= 0.5 else t, z_of = lambda t: t if t >= 0.5 else 0.5)
pointyCone = overallShape(r_of = lambda t: t**2, z_of = lambda t: 10*t, t_f = 1)
parabola = overallShape(r_of = identity, z_of = lambda t: t**2)

# sphere shapes
hemiSphere = overallShape(r_of = absinthe, z_of = cos, dMod = 1)
sphere = overallShape(r_of = absinthe, z_of = cos, dMod = 2.0)
smallSphere = overallShape(r_of = absinthe, z_of = cos, dMod = 4.0)
safeSphere = overallShape(r_of = absinthe, z_of = lambda t: cos(t) + 1.001, dMod = 2)

# torus shapes
torus = overallShape(r_of = lambda t: sin(t) + 2, z_of = cos, t_f = tau)
spiralTorus = overallShape(r_of = lambda t: abs(sin(t) * (30 / (t + 30)) + 2), z_of = lambda t: cos(t) * (30 / (t + 30)), t_f = 8*tau)
spindleTorus = overallShape(r_of = lambda t: abs(sin(t) + 0.7), z_of = lambda t: cos(t), t_f = tau)
phatTorus = overallShape(r_of = lambda t: sin(t) + 1.1, z_of = lambda t: cos(t), t_f = tau)
safeTorus = overallShape(r_of = lambda t: sin(t) + 2, z_of = lambda t: cos(t) + 1.001, dMod = tau*2)

# hybrid shapes
weirdThing1_o = geoBlend(cone, safeSphere, 0.4)
weirdThing1 = geoBlend(cone, safeSphere, ratio = 0.4, max_dt = 1E-2)
weirdThing2 = arithBlend(safeTorus, cappedCylinder, ratio = 0.4, dA_i = 0.1)

# misc shapes
ridges = overallShape(r_of = lambda t: sin(t) + 5, z_of = lambda t: t + 0.1, dMod = 100)
heartShape = overallShape(r_of = lambda t: 1 - cos(t), z_of = lambda t: (-sin(t) if t < pi else t - pi), dMod = tau*7/6, max_dt = 0.05)

# Rotations
offAxis = Rotation(initialQuaternion = (0, 1, 0, 0), moveAngle = (0, 1, 0), speed = 0.05)
offAxisSlow = Rotation(initialQuaternion = (0, 1, 0, 0), moveAngle = (0, 1, 0), speed = 0.01)
christmasTree = Rotation(initialQuaternion = (2**-0.5, 2**-0.5, 0, 0), speed = 0)
spinningTree = Rotation(initialQuaternion = (2**-0.5, 2**-0.5, 0, 0), moveAngle = (0, 1, 0), speed = 0.01)
headOnSpin = Rotation(initialQuaternion = (0, 0, 0, 1), moveAngle = (0, 0, 1), speed = 0.001)
noRotation = Rotation(initialQuaternion = (0, 0, 0, 1), speed = 0)

# Preset animations I happen to like
def flowTorus():
  animate(shape = spiralTorus, mutators = [mutators().oscillatingTheta(tau/sqrt(2), 1E-3, 0.1)], rotation = offAxisSlow, n = 400)
def zaWorudo():
  animate(shape = sphere, mutators = [mutators().oscillatingTheta(tau * (19/99), 1E-3, 0.1)], rotation = spinningTree, n = 400)
def spiralsTorus():
  animate(shape = torus, mutators = [mutators().oscillateShape(50, 50, 1E-2)], rotation = offAxisSlow, n = 400)
def flexingDivot():
  animate(shape = weirdThing1, mutators = [mutators().oscillateShape(pi/2, pi/2, 0.1)], rotation = offAxisSlow, n = 400)
def heart():
  animate(shape = heartShape, mutators = [mutators().oscillatingTheta(tau/2, 0.1, 1E-3)], rotation = spinningTree, n = 400)
def xmas():
  animate(shape = pointyCone, mutators = [mutators().deltaTheta(1E-4)], rotation = spinningTree, n = 200)
def sunflower():
  animate(shape = plane, mutators = [mutators().fixedTheta(sqrt(2)*pi)], rotation = headOnSpin, n = 400)

# import cProfile
# cProfile.run('sunflower()')

spiralsTorus()
