class Rotation:
  """
  Rotation class

  Defines how the points are rotated each tick, before being viewed.

  Properties:
  initialQuaternion (tuple(float|int, float|int, float|int, float|int): the angle to start at
  moveAngle (tuple(4, float|int)): axis of rotation
  speed (float): number of rotations about moveAngle per tick
  """
  def __init__(self, initialQuaternion = (1, 0, 0, 0), moveAngle = (1, 0, 0), speed = 0.005):
    self.moveAngle = moveAngle
    self.initialQuaternion = initialQuaternion
    self.speed = speed

offAxis = Rotation(initialQuaternion = (0, 1, 0, 0), moveAngle = (0, 1, 0), speed = 0.05)
offAxisSlow = Rotation(initialQuaternion = (0, 1, 0, 0), moveAngle = (0, 1, 0), speed = 0.01)
christmasTree = Rotation(initialQuaternion = (2**-0.5, 2**-0.5, 0, 0), speed = 0)
spinningTree = Rotation(initialQuaternion = (2**-0.5, 2**-0.5, 0, 0), moveAngle = (0, 1, 0), speed = 0.01)
headOnSpin = Rotation(initialQuaternion = (0, 0, 0, 1), moveAngle = (0, 0, 1), speed = 0.001)
noRotation = Rotation(initialQuaternion = (0, 0, 0, 1), speed = 0)