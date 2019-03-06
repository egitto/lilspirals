from math import sin, pi, sqrt
tau = 2 * pi

def theta(initial = sqrt(2)*pi, delta = 0):
  # pretty values for theta to be constant at: 2.33068600268, sqrt(2)*pi, sqrt(10)*pi, 2.32324311855, 4.62290939916, 20.7563962399, 2.32120903841
  def fxn(texture, i, **kwargs):
    texture.theta = initial + i * delta
  return fxn

def oscillatingTheta(theta, amp, freq):
  def fxn(texture, i, **kwargs):
    texture.theta = theta + tau * amp * sin(i * freq)
  return fxn

def expandShape(initial, delta = 0.):
  def fxn(shape, i, **kwargs):
    shape.t_f = initial + i * delta
  return fxn

def oscillateShape(center, amp, freq):
  def fxn(shape, i, **kwargs):
    shape.t_f = center + amp * sin(i * freq)
  return fxn

def oscillate_t_i(center, amp, freq):
  def fxn(shape, i, **kwargs):
    shape.t_i = center + amp * sin(i * freq)
  return fxn

def adjust_dA_i(shape, **kwargs):
  shape.dA_i += 0.1

def force_dt(shape, **kwargs):
  shape.max_dt += 0.05