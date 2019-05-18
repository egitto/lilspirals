# What is it
When run, it prints pretty spirals in your terminal.

# Requirements:
Python 2 or 3, `numpy`, `transforms3d`

# How to use:
```
git clone https://github.com/egitto/lilspirals
cd lilspirals
pip install numpy && pip install transforms3d
./main.py
```

# Screenshots:
![gif of globe](../master/gifs/globe.gif)
![gif of heart](../master/gifs/heart.gif)
![gif of torus](../master/gifs/torus.gif)

# Tips
Pass different pre-written shapes and rotations to `animate` on the last line to see different patterns

Make different custom shapes; see references.
- Blending existing shapes with blendShapes
- Define new shapes with `Shape` constructor, passing in custom `r_of` and `z_of` functions
- Use t_i and t_f* to fit the domain of the r_of and z_of functions
  - caveat: the desired t_f is achieved by iteratively adjusting dMod, which is not perfect
    - if you have a better solution let me know

Several different rotations are predefined
- `offAxis` is useful for seeing what a shape actually looks like, rotating it perpendicular to its primary symmetry axis
- `spinningTree` is nice and pretty, showing it from its side as it rotates on its primary symmetry axis
- `noRotation` and `headOnSpin` are nice for when you want to look at radially symmetrical patterns

# Further ideas (todos?):
- A better rendering system than just dumping output into a terminal
  - ncurses?
  - output to png or jpg?
  - output to animated gif? (ideally via pipe)
  - display as a legit animation that accepts input (openGL?) 
    - must be cross-platform
- Translate to js, run in browser? (rendered, not via `console.log`)
- Make it a Jupyter notebook?
- Better documentation
- Interactivity
  - rotate or adjust theta via user input
  - rotate along all axes, while it keeps slowly changing
  - blend between different shapes smoothly
    - will need a lot of refactoring, but could be pretty cool
- More general blendShapes, that takes more shapes as input
