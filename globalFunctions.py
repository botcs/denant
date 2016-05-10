import numpy as np


def dist(p1, p2):
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def findNearest(array, value):
    idx = np.searchsorted(array, value, side="left")
    if idx == len(array) or \
       np.abs(value - array[idx - 1]) < np.abs(value - array[idx]):
        return idx - 1
    else:
        return idx
