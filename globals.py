import numpy as np
import os

'''GLOBALLY USED VARIABLES AND FUNCTIONS FOR THE PERIOD OF EACH RUN'''

'Flags'
verbose = False
cartesian = False
separated = False
versus = False

'Main parameters'
inputs = []
binn = []
rad = []
res = 0
output = []



RESOLUTION = 0
axes = ([], [], [])
bounds = ([], [], [])
DELTA = 0
TotalPoints = 0



def printVerbose(string):
    if verbose is True:
        print(string)

def ensure_dir(f):

    d = os.path.dirname(f+'/')

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
    output = args.output
    
    
