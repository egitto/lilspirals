from math import sin, cos

def rPointFactory(z_of, r_of):
  """Factory for the rPoint class

  Params:
  z_of: see Shape.z_of
  r_of: see Shape.r_of
  """
  # spec = [(x, float32) for x in 'r,theta,t,x,y,z'.split(',')]
  # @jitclass(spec)
  class rPoint:
    """A single point

    Properties:
    r (float): distance from primary axis (radius). equal to r_of(t)
    theta (float): rotation of point around axis
    t (float): distance along path described by r_of and z_of
    x (float): horizontal position in space
    y (float): vertical position in space
    z (float): depth in space. equal to z_of(t).
    """
    def __init__(self, theta, t = 0.):
      """Constructor for the rPoint class

      Params:
      theta (float): angle to rotate about primary axis
      t (float): value passed to r_of and z_of. See Shape
      """
      # Given floats t and theta, finds the proper r and z values,
      # and transforms those r and z values into xyz coordinates.
      self.r = r_of(t)
      self.theta = theta
      self.t = t
      self.x = cos(self.theta)*self.r
      self.y = sin(self.theta)*self.r
      self.z = z_of(t)
    def xy_pos(self):
      """Returns tuple (x, y)"""
      return (self.x, self.y)
    def xyz_pos(self):
      """Returns tuple (x, y, z)"""
      return (self.x, self.y, self.z)
    def __repr__(self):
      return str((self.x,self.y,self.z))
  return rPoint

def makePoints(dTheta, n, shape):
  """Produces array of rPoints mapped onto shape

  Params:
  dTheta (float): amount to increase theta between each point
  n (int): number of points to render
  shape (Shape): Shape defining surface to map points onto
  """
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