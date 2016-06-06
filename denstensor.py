import numpy as np
import pandas as pd
import os

import globals

findNearestIndex = globals.findNearest
vprint = globals.printVerbose


def getTresholdedVolumeMeasure(tensor, treshold):
    return np.count_nonzero(tensor > treshold) * globals.DELTA


class PointSet:

    def __init__(self, D, B, I):
        '''init with outer file'''
        self.DENSITY_RADIUS = D
        self.BINSTEPS = B
        self.IN_FILE = I
        if globals.verbose:
            vprint('Reading in file:   ' + self.IN_FILE)
        self.read3DPoints()

        head, tail = os.path.split(self.IN_FILE)
        tail, ext = os.path.splitext(tail)
        self.name = tail + '-rad' + \
            str(self.DENSITY_RADIUS) + '-bin' + str(self.BINSTEPS)

    '''
    def __init__(self, D, B, A, name):
        self.DENSITY_RADIUS = D
        self.BINSTEPS = B
        self.IN = pd.DataFrame(A)
        self.name = name
    '''

    # I/O SUPPORT FUNCTIONS ###
    def read3DPoints(self):

        try:
            self.IN = pd.read_csv(self.IN_FILE, delimiter='\t')
        except IOError as e:
            vprint(e.message)
            vprint('Skipping this set...')
            raise

        globals.TotalPoints += len(self.IN.index)

    def checkDimension(self):
        '''CHECKS GLOBAL DIMENSIONS FOR DATA SET one session handles every
        point, regarding the largest density sphere in an equally
        large space to be able to sum their densities if needed

        in other words the edges of the space are global for ALL IN
        ALL SETS

        returns true if the dimension is modified returns false if no
        modification executed

        '''
        edge = self.DENSITY_RADIUS

        if globals.verbose:
            globals.printHeader('Checking dimensions for ' + self.name)
        bounds = (
            [self.IN.X.min() - edge,
             self.IN.X.max() + edge],

            [self.IN.Y.min() - edge,
             self.IN.Y.max() + edge],

            [self.IN.Z.min() - edge,
             self.IN.Z.max() + edge]
        )

        axisX = globals.axes[0]
        axisY = globals.axes[1]
        axisZ = globals.axes[2]

        # any(globals.axes) should work as an emptiness check...
        # but it doesn't... dunno y =(
        if any(globals.axes[0]):
            if (not (bounds[0][0] < axisX[0] or bounds[0][1] > axisX[-1] or
                     bounds[1][0] < axisY[0] or bounds[1][1] > axisY[-1] or
                     bounds[2][0] < axisZ[0] or bounds[2][1] > axisZ[-1])):
                vprint('--> No space extension needed')
                return False
            else:
                vprint('--> Extending axes')
                # vprint('\n  Old aparametres:')
                # PointSet.printBounds()
                for i in (0, 1, 2):
                    bounds[i][0] = min(bounds[i][0], globals.axes[i][0])
                    bounds[i][1] = max(bounds[i][1], globals.axes[i][-1])
        else:
            vprint('--> Bounds not initialised yet')

        intervals = (
            bounds[0][1] - bounds[0][0],
            bounds[1][1] - bounds[1][0],
            bounds[2][1] - bounds[2][0]
        )

        DELTA = min(intervals) / float(globals.res)
        globals.DELTA = DELTA
        globals.axes = (
            np.linspace(bounds[0][0], bounds[0][1], intervals[0] / DELTA),
            np.linspace(bounds[1][0], bounds[1][1], intervals[1] / DELTA),
            np.linspace(bounds[2][0], bounds[2][1], intervals[2] / DELTA)
        )

        vprint("\n  Space expanded with new parametres:")
        PointSet.printBounds()

        return True

    # STATUS MONITORING ###
    @classmethod
    def printBounds(cls):
        for i, W in enumerate('XYZ'):
            vprint("{} axis [start, end, length]:\n\t{}\t{}\t{}\t".format(
                W, globals.axes[i][0], globals.axes[i][-1], len(globals.axes[i])))

    def printOpts(self):
        print('\tOptions for this set:\t')
        print('\tBINNING STEPS:\t{}'.format(self.BINSTEPS))
        print('\tDENS RADIUS:\t{}'.format(self.DENSITY_RADIUS))
        print('\tRESOLUTION:\t{}'.format(globals.res))

    def coarseErr(self):
        vprint('\nProblem: grid is too coarse, increment resolution!!')
        return True
        #exit('coarse error')

    # MAIN CALCULATION FUNCTIONS ###

    def setSampleDensity(self):
        ''' SAMPLE DENSITY IS COPIED FOR EACH POINT IN SET'''
        vprint("Constructing new Sample density... ")

        R = self.DENSITY_RADIUS

        def evalDens(x, y, z):
            return max(globals.dens(R, globals.norm([x, y, z])), 0)
        # localMesh ##
        side = np.arange(-R, R, globals.DELTA)
        mX, mY, mZ = np.meshgrid(side, side, side)
        try:
            self.sampleTens = np.vectorize(
                evalDens)(mX, mY, mZ)[1:-1, 1:-1, 1:-1]
        except IndexError:
            self.coarseErr()
            raise

        if np.count_nonzero(self.sampleTens > 0) < 5:
            return self.coarseErr()
        else:
            vprint("\bDone")

    def getDensityTensor(self):
        if self.checkDimension():
            self.setDensityTensor()
        return self.D

    def getBinned(self):
        self.binterval = globals.getBinterval(self.D, self.BINSTEPS)

        def binVal(x):
            return self.interval[globals.findNearest(self.binterval, x)]

        return np.vectorize(binVal)(self.D)

    def getBinVols(self):
        '''Return an array with the volumes of the thresholded density tensor

        Points with density over the thresholded level are
        evaluated as true and then these entries are counted.
        The results are multiplied with the delta of the tensor's grid
        (the physical distance between two neighbouring point)
        '''
        self.binterval = globals.getBinterval(self.D, self.BINSTEPS)
        self.binVols = []
        for binstep in self.binterval:
            self.binVols.append(getTresholdedVolumeMeasure(self.D, binstep))
        return self.binVols

    def setDensityTensor(self):
        if globals.verbose:
            globals.printHeader(
                'Calculating density tensor for ' + self.name)
            self.printOpts()

        if self.setSampleDensity():
            '''Sample density construction failed, skip filling with 0'''
            return False

        axesLen = np.vectorize(len)(globals.axes)
        vprint('Allocating memory, total: {} entries'.format(
            np.prod(axesLen)))
        self.D = np.zeros(axesLen, dtype=np.float)
        vprint("Calculating density tensor")
        if globals.verbose:
            bar = globals.StatusBar(len(self.IN.index))
        for P in self.IN[['X', 'Y', 'Z']].values:
            if globals.verbose:
                bar.update()
            # top left coordinates ###
            C = (P[0] - self.DENSITY_RADIUS,
                 P[1] - self.DENSITY_RADIUS,
                 P[2] - self.DENSITY_RADIUS)

            xFrom = findNearestIndex(globals.axes[0], C[0])
            yFrom = findNearestIndex(globals.axes[1], C[1])
            zFrom = findNearestIndex(globals.axes[2], C[2])
            xTo = xFrom + self.sampleTens.shape[0]
            yTo = yFrom + self.sampleTens.shape[1]
            zTo = zFrom + self.sampleTens.shape[2]

            try:
                self.D[xFrom:xTo, yFrom:yTo, zFrom:zTo] += self.sampleTens
            except ValueError:
                self.coarseErr()
                self.printBounds()
                raise

        return True
