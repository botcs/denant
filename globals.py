import numpy as np
import os
import sys

'''GLOBALLY USED VARIABLES AND FUNCTIONS FOR THE PERIOD OF EACH RUN'''

'Flags'
verbose = False
cartesian = False
separated = False
versus = None

'Main parameters'
inputs = []
binn = [3]
rad = [3000]
res = 50
output = 'default_output'


'Point Set globals'
RESOLUTION = 0
axes = ([], [], [])
bounds = ([], [], [])
DELTA = 0
TotalPoints = 0


class StatusBar:

    def __init__(self, total, barLength=30):
        self.total = total
        self.curr = 0
        self.percentage = 0
        self.barLength = barLength

    def barStr(self):
        currBar = self.barLength * self.percentage / 100
        return '[' + "=" * currBar + " " * (self.barLength - currBar) + ']'

    def printBar(self):
        if(self.percentage <= 100):
            print("\r  " + self.barStr() + "  Done/Total (" +
                  str(self.curr) + '/' + str(self.total) + ")   " +
                  str(100 * self.curr / self.total) + "%     "),
            sys.stdout.flush()
            if(self.percentage == 100):
                print '\n'

    def update(self):
        self.curr += 1
        currPercentage = self.curr * 100 / self.total
        if(currPercentage > self.percentage):
            self.percentage = currPercentage
            self.printBar()


def printHeader(h):

    hBar = len(h) * '-'
    print '\n' + hBar
    print h
    print hBar


def printVerbose(string):
    if verbose is True:
        print(string)


def ensure_dir(f):

    d = os.path.dirname(f + '/')

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


def initFromPrompt():
    '''Load global parameters from prompt
    Using promptParser module'''

    'Flags'
    global verbose
    global cartesian
    global separated
    global versus

    'Main parameters'
    global inputs
    global binn
    global rad
    global res
    global output

    import promptParser
    args = promptParser.parse()

    verbose = args.verbose
    cartesian = args.cartesian
    separated = args.separated
    versus = args.versus

    inputs = args.inputs
    binn = args.binn
    rad = args.rad
    res = args.res
    output = args.output[0]
