from numpy import array
from math import sqrt

class Shape:
  """The shape of the surface that will be covered in points

  Properties:
  r_of (lambda t: radius) radius from center, given t where t increases monotonically with point number.
  z_of (lambda t: depth) depth from origin, given t where t increases monotonically with point number.
  dA_i (float): initial value of dA, for fine-tuning
  t_i (float): initial value of t. Should be > 0.
  t_f (float): ideal final value of t. Should be > t_i.
  max_dt (float): largest allowable value of t_(n+1) - t_n
  dMod (float): inverse density modifier, because some shapes work best with different densities.
    higher dMod = less dense, so t will reach higher values
  """
  def __init__(self, dA_i = 1, r_of = False, z_of = False, dMod = 1., name = 'unnamed', t_f = 0., t_i = 0., max_dt = 9E99):
    """Initializer for the Shape class"""
    self.r_of = r_of if r_of else lambda t: t
    self.z_of = z_of if z_of else lambda t: t
    self.dA_i = dA_i * 1.0
    self.dMod = dMod * 1.0
    self.t_f = t_f * 1.0
    self.t_i = t_i * 1.0
    self.max_dt = max_dt * 1.0
    self.name = name
  def adjustDensity(self, points):
    """Mutate dMod to try to achieve t_f

    Params:
    Points (rPoint[]): the points produced by this shape on the previous tick
    """
    if not self.t_f: return
    ratio = (self.t_f / points[-1].t)
    # overshot goal (big ratio)? decrease density (increase dMod)
    self.dMod *= sqrt(ratio) # sqrt to prevent oscillations
  def get_dt(self, density, dt, r, dr, dz):
    """Figure out how much to increment t between points
    """
    # choose dt to achieve fixed dA of 1/density
    # assumption: dA is proportional to dt
    goal_dA = self.dMod / density # m^2 / point
    dA = r * sqrt(dz**2 + dr**2) # m^2 (technically we dropped a 2pi, but w/e)
    dA = dA if dA else self.dA_i # the first time, we won't have any data
    # square root is just for damping, don't want to over-adjust
    goal_dt = dt * sqrt(goal_dA / dA)
    return min(self.max_dt, goal_dt)

def geoBlend(s1, s2, ratio = 0.5, **kwargs):
  """Produce the geometric mean of two shapes

  Params:
  s1 (Shape): x such that for all t > 0, x.r_of(t) > 0 and x.z_of(t) > 0
  s2 (Shape): same as s1
  ratio (float): number between 0 and 1 (exclusive)
  """
  def blendFxns(f1, f2):
    return lambda t: (f1(t) ** ratio) * (f2(t) ** (1 - ratio))
  r_of = blendFxns(s1.r_of, s2.r_of)
  z_of = blendFxns(s1.z_of, s2.z_of)
  return Shape(r_of = r_of, z_of = z_of, **kwargs)

def arithBlend(s1, s2, ratio = 0.5, **kwargs):
  """Produce the arithmetic mean of two shapes

  Params:
  s1 (Shape)
  s2 (Shape)
  ratio (float): number between 0 and 1 (exclusive)
  """
  def blendFxns(f1, f2):
    return lambda t: (f1(t) * ratio) + (f2(t) * (1 - ratio))
  r_of = blendFxns(s1.r_of, s2.r_of)
  z_of = blendFxns(s1.z_of, s2.z_of)
  return Shape(r_of = r_of, z_of = z_of, **kwargs)

# not used anywhere, on account of nonperformance
class shapeFactory:
  def __init__(self, shapes, weights, dA_i = 1, dMod = 1):
    # shapes: an array of elementary shape objects
    # weights: an array of same length, of nonzero non-negative numbers
    self.shapes = array(shapes)
    self.weights = array(weights)
    self.updateProps()
  def getShape(self):
    return Shape(self.dA_i, self.r_of, self.z_of, self.dMod)
  def blendFxns(self, fs):
    if len(fs) == 1: return fs[0]
    ws = self.weights / self.weights.sum()
    z = zip(fs,ws)
    return lambda t: array([f(t) ** w for f, w in zip(fs, ws)]).prod() # this is weirdly slow
  def updateProps(self):
    self.r_of = self.blendFxns(array([s.r_of for s in self.shapes]))
    self.z_of = self.blendFxns(array([s.z_of for s in self.shapes]))
  def addShape(self, shape):
    self.shapes = append(self.shapes, shape)
    self.weights = append(self.weights, 0)
    self.updateProps
  def removeShape(self, i):
    if self.weights[i] != 0: return false
    self.shapes = append(self.shapes[:i], self.shapes[i+1:])
    self.weights = append(self.weights[:i], self.weights[i+1:])
    self.updateProps()
  def incrWeight(self, d_weights):
    self.weights = self.weights + d_weights