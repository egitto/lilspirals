#!/usr/bin/python
from math import pi, sin, cos, sqrt, sinh, cosh
import time
from transforms3d import quaternions as quats
import sys
import mutators
from points import rPointFactory, makePoints
from view import ViewPoints, screenSingleton
from shape import Shape, geoBlend, arithBlend
from rotations import offAxis, offAxisSlow, christmasTree, spinningTree, headOnSpin, noRotation
import curses
from input import handleInput

tau = 2*pi

class Texture:
  # this gets a class so that mutators can affect it
  def __init__(self, theta):
    self.theta = theta

def _animate(shape, rotation, mutators = [], delay = .15, n = 400, size = (170,70), smooth = 4.):
  """
  Animates the shape passed in into the console

  Parameters:
  shape (Shape): The shape to render
  rotation (Rotation): How the object should rotate within the view
  delay (float): seconds between ticks
  n (int > 0): number of points to render
  size (tuple(int > 0, int > 0)): size of the view, in characters
  smooth (float): frames per tick
  """
  i = 1
  q = rotation.initialQuaternion
  rotateBy = quats.axangle2quat(rotation.moveAngle, rotation.speed*tau/smooth)
  texture = Texture(theta = tau/sqrt(2))
  paused = False
  while True:
    frameStart = time.time()
    ch = screenSingleton.getch()
    ch, q, i, paused = handleInput(ch, q, i, paused)
    [mut(shape = shape, i = i/smooth, texture = texture) for mut in mutators]
    points = makePoints(texture.theta, n, shape)
    shape.adjustDensity(points)
    ViewPoints(points, size, rotateQuaternion = q).render()
    if not paused: i += 1
    frameDuration = time.time() - frameStart
    sleepTime = delay/smooth - max(0, frameDuration)
    if sleepTime > 0: time.sleep(sleepTime)

def animate(*args, **kwargs):
  try:
    _animate(*args, **kwargs)
  except:
    curses.echo()
    curses.nocbreak()
    curses.endwin()
    raise

def identity(t):
  """Returns t"""
  return t

def absinthe(t):
  """Absolute value of sin of t"""
  return abs(sin(t))

# Example basic shapes

plane = Shape(r_of = identity, z_of = lambda t: 0)
cone = Shape(r_of = identity, z_of = identity)
cylinder = Shape(r_of = lambda t: 0.5, z_of = identity)
cappedCylinder = Shape(r_of = lambda t: 0.5 if t >= 0.5 else t, z_of = lambda t: t if t >= 0.5 else 0.5)
pointyCone = Shape(r_of = lambda t: t**2, z_of = lambda t: 10*t, t_f = 1)
parabola = Shape(r_of = identity, z_of = lambda t: t**2)

# sphere shapes

hemiSphere = Shape(r_of = absinthe, z_of = cos, dMod = 1)
sphere = Shape(r_of = absinthe, z_of = cos, dMod = 2.0)
smallSphere = Shape(r_of = absinthe, z_of = cos, dMod = 4.0)
safeSphere = Shape(r_of = absinthe, z_of = lambda t: cos(t) + 1.001, dMod = 2)

# torus shapes

torus = Shape(r_of = lambda t: sin(t) + 2, z_of = cos, t_f = tau)
spiralTorus = Shape(r_of = lambda t: abs(sin(t) * (30 / (t + 30)) + 2), z_of = lambda t: cos(t) * (30 / (t + 30)), t_f = 8*tau)
spindleTorus = Shape(r_of = lambda t: abs(sin(t) + 0.7), z_of = lambda t: cos(t), t_f = tau)
phatTorus = Shape(r_of = lambda t: sin(t) + 1.1, z_of = lambda t: cos(t), t_f = tau)
safeTorus = Shape(r_of = lambda t: sin(t) + 2, z_of = lambda t: cos(t) + 1.001, dMod = tau*2)

# hybrid shapes

weirdThing1_o = geoBlend(cone, safeSphere, 0.4)
weirdThing1 = geoBlend(cone, safeSphere, ratio = 0.4, max_dt = 1E-2)
weirdThing2 = arithBlend(safeTorus, cappedCylinder, ratio = 0.4, dA_i = 0.1)

# misc shapes

ridges = Shape(r_of = lambda t: sin(t) + 5, z_of = lambda t: t + 0.1, dMod = 100)
heartShape = Shape(r_of = lambda t: 1 - cos(t), z_of = lambda t: (-sin(t) if t < pi else t - pi), dMod = tau*7/6, max_dt = 0.05)

# Preset animations I happen to like

def flowTorus():
  """Animates spiralTorus with oscillatingTheta"""
  animate(shape = spiralTorus, mutators = [mutators.oscillatingTheta(tau/sqrt(2), 1E-3, 0.1)], rotation = offAxisSlow, n = 400)
def zaWorudo():
  """Animates sphere with oscillatingTheta"""
  animate(shape = sphere, mutators = [mutators.oscillatingTheta(tau * (19/99), 1E-3, 0.1)], rotation = spinningTree, n = 400)
def spiralsTorus():
  """Animates a particularly lovely torus"""
  animate(shape = torus, mutators = [mutators.oscillateShape(50 + tau, 50, 1E-2)], rotation = offAxis, n = 400)
def flexingDivot():
  """Animates a weird moving shape"""
  animate(shape = weirdThing1, mutators = [mutators.oscillateShape(pi/2, pi/2, 0.1)], rotation = offAxisSlow, n = 400)
def heart():
  """Animates a spinning heart (or perhaps a beet)"""
  animate(shape = heartShape, mutators = [mutators.oscillatingTheta(pi, 0.1, 1E-3)], rotation = spinningTree, n = 400)
def xmas():
  """Animates something like a christmas tree"""
  animate(shape = pointyCone, mutators = [mutators.theta(delta = 1E-4)], rotation = spinningTree, n = 200)
def sunflower():
  """Animates an ordinary circle, slowly rotating"""
  animate(shape = plane, mutators = [mutators.theta(initial = sqrt(2)*pi)], rotation = headOnSpin, n = 400)

import cProfile
cProfile.run('spiralsTorus()')

# spiralsTorus()
