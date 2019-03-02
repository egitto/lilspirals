#!/usr/bin/python
from math import e, pi, sin, cos, sqrt, sinh, cosh
from numpy import array, matrix, dot, append, product, log, exp
import time
from transforms3d import quaternions as quats
import sys
import mutators
from points import rPointFactory, makePoints
from view import ViewPoints
from shape import overallShape, geoBlend, arithBlend
from rotations import offAxis, offAxisSlow, christmasTree, spinningTree, headOnSpin, noRotation

tau = 2*pi

class Texture:
  # this gets a class so that mutators can affect it
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

# Preset animations I happen to like
def flowTorus():
  animate(shape = spiralTorus, mutators = [mutators.oscillatingTheta(tau/sqrt(2), 1E-3, 0.1)], rotation = offAxisSlow, n = 400)
def zaWorudo():
  animate(shape = sphere, mutators = [mutators.oscillatingTheta(tau * (19/99), 1E-3, 0.1)], rotation = spinningTree, n = 400)
def spiralsTorus():
  animate(shape = torus, mutators = [mutators.expandShape(5E-2)], rotation = offAxisSlow, n = 400)
def flexingDivot():
  animate(shape = weirdThing1, mutators = [mutators.oscillateShape(pi/2, pi/2, 0.1)], rotation = offAxisSlow, n = 400)
def heart():
  animate(shape = heartShape, mutators = [mutators.oscillatingTheta(tau/2, 0.1, 1E-3)], rotation = spinningTree, n = 400)
def xmas():
  animate(shape = pointyCone, mutators = [mutators.deltaTheta(1E-4)], rotation = spinningTree, n = 200)
def sunflower():
  animate(shape = plane, mutators = [mutators.fixedTheta(sqrt(2)*pi)], rotation = headOnSpin, n = 400)

# import cProfile
# cProfile.run('flexingDivot()')

spiralsTorus()
