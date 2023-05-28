import math
from math import *
from mindustry import *
from templates import *

def_poids = {Blocks.copper_wall: 1, Blocks.titanium_wall: 3, Blocks.duo: 2, Blocks.scatter: 3}


def dist(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


# Retourne la valeur du centre des défense adverse et la variance (la somme des distance au centre au carré)
def center_def(defense, world):
    s = 0
    xc, yc = id_to_coord(defense[0])
    block = world[yc][xc].block
    p = def_poids[block]
    s += p
    xc *= p
    yc *= p
    for i in range(1, len(defense)):
        x, y = id_to_coord(defense[i])
        p = def_poids[world[y][x].block]
        s += p
        xc += x * p
        yc += y * p
    xc = xc / s
    yc = yc / s

    variance = 0
    for i in range(len(defense)):
        x, y = id_to_coord(defense[i])
        variance += dist(x, y, xc, yc)

    return xc, yc, variance
