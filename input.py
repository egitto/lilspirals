from transforms3d import quaternions as quats

right = quats.axangle2quat((0, 1, 0), 0.1);
smallRight = quats.axangle2quat((0, 1, 0), 0.02);

left = quats.axangle2quat((0, 1, 0), -0.1);
smallLeft = quats.axangle2quat((0, 1, 0), -0.02);

up = quats.axangle2quat((1, 0, 0), -0.1);
smallUp = quats.axangle2quat((1, 0, 0), -0.02);

down = quats.axangle2quat((1, 0, 0), 0.1);
smallDown = quats.axangle2quat((1, 0, 0), 0.02);

def handleInput(ch, q, i, paused):
    if ch == -1: return (ch, q, i, paused)
    c = chr(ch)

    if (c == 'a'): q = quats.qmult(q, left)
    elif (c == 'A'): q = quats.qmult(q, smallLeft)
    elif (c == 'd'): q = quats.qmult(q, right)
    elif (c == 'D'): q = quats.qmult(q, smallRight)
    elif (c == 'w'): q = quats.qmult(q, up)
    elif (c == 'W'): q = quats.qmult(q, smallUp)
    elif (c == 's'): q = quats.qmult(q, down)
    elif (c == 'S'): q = quats.qmult(q, smallDown)
    elif (c == 'z'): i -= 1
    elif (c == 'c'): i += 1
    elif (c == ' '): paused = not paused;

    return (ch, q, i, paused)