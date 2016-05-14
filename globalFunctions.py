import numpy as np
import os
import promptParser


def printVerbose(string):
    if promptParser.args.verbose is True:
        print(string)


def ensure_dir(f):

    # correction of input (e.g. path/to/dir/  VS path/to/dir )#
    f += '/'

    d = os.path.dirname(f)

    printVerbose('Checking output path...  ')
    if not os.path.exists(d):
        printVerbose('Making directory:\n\t{}'.format(d))
        try:
            os.makedirs(d)
        except OSError as e:
            print 'Cannot make directory ', e
            exit('dirmake: permission denied')
    else:
        printVerbose('OK, Directory exists:\n\t{}'.format(d))

norm = np.linalg.norm


def getBinterval(T, steps):
        maxVal = np.max(T)
        minVal = np.min(T)
        '''everything is truncated to the lowest value
        so the max value is always yields zero measure
        when tresholding'''

        return np.linspace(minVal, maxVal + 0.001, steps + 1)[:-1]


def dens(DENSITY_RADIUS, r):
    return DENSITY_RADIUS - r


def findNearest(array, value):
    idx = np.searchsorted(array, value, side="left")
    if idx == len(array) or \
       np.abs(value - array[idx - 1]) < np.abs(value - array[idx]):
        return idx - 1
    else:
        return idx
