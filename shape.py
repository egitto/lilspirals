from numpy import array
from math import sqrt

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

# not used anywhere, on account of nonperformance
class shapeFactory:
  def __init__(self, shapes, weights, dA_i = 1, dMod = 1):
    # shapes: an array of elementary shape objects
    # weights: an array of same length, of nonzero non-negative numbers
    self.shapes = array(shapes)
    self.weights = array(weights)
    self.updateProps()
  def getShape(self):
    return overallShape(self.dA_i, self.r_of, self.z_of, self.dMod)
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