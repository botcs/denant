import numpy as np
import os
import promptParser


def printVerbose(string):
    if promptParser.args.verbose is True:
        print(string)


def ensure_dir(f):

    # correction of input (e.g. path/to/dir/  VS path/to/dir )#
    f += '/'

    print f
    d = os.path.dirname(f)

    print 'Checking output path...  '
    if not os.path.exists(d):
        print 'Making directory: {}'.format(d)
        os.makedirs(d)
    else:
        print 'OK, Directory exists: {}'.format(d)


def dist(p1, p2):
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def findNearest(array, value):
    idx = np.searchsorted(array, value, side="left")
    if idx == len(array) or \
       np.abs(value - array[idx - 1]) < np.abs(value - array[idx]):
        return idx - 1
    else:
        return idx
