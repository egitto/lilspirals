from math import sin, cos

def rPointFactory(z_of, r_of):
  # Factory for the rPoint class, just because I want to define the shape
  # functions z_of and r_of elsewhere
  # spec = [(x, float32) for x in 'r,theta,t,x,y,z'.split(',')]
  # @jitclass(spec)
  class rPoint:
    def __init__(self, theta, t = 0.):
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