import numpy as np
import pandas as pd

import Visualizer as v
import globalFunctions as gf
import promptParser

findNearestIndex = gf.findNearest
vprint = gf.printVerbose
verbose = promptParser.args.verbose


class PointSet:

    def __init__(self, D, I, B):
        # METAPARAMETERS ###
        self.DENSITY_RADIUS = D
        self.IN_FILE = I
        self.BINSTEPS = B
        self.binVols = []
        if verbose:
            v.printHeader('Reading in file:   ' + self.IN_FILE)
        try:
            self.IN = pd.read_csv(self.IN_FILE, delimiter='\t')
        except IOError as e:
            vprint(e.message)
            vprint('Skipping this set...')
            raise

    # GLOBAL VARIABLES ###
    RESOLUTION = 0
    axes = ([], [], [])
    bounds = ([], [], [])
    DELTA = 0
    TotalPoints = 0

    # I/O SUPPORT FUNCTIONS ###
    def read3DPoints(self):
        self.pointList = self.IN[['X', 'Y', 'Z']].values
        PointSet.TotalPoints += len(self.pointList)
        vprint("Reading {} point finished, total count: {}".format(
            len(self.pointList), PointSet.TotalPoints))

    def checkDimension(self):
        # CHECKS GLOBAL DIMENSIONS FOR DATA SET
        # one session handles every point, regarding the largest density sphere
        # in an equally large space to be able to sum their densities if needed

        # in other words the edges of the space are global for ALL
        # IN ALL SETS

        # returns true if the dimension is modified
        # returns false if no modification executed

        edge = self.DENSITY_RADIUS

        vprint('Checking global dimensions...')
        bounds = (
            [self.IN.X.min() - edge,
             self.IN.X.max() + edge],

            [self.IN.Y.min() - edge,
             self.IN.Y.max() + edge],

            [self.IN.Z.min() - edge,
             self.IN.Z.max() + edge]
        )

        axisX = PointSet.axes[0]
        axisY = PointSet.axes[1]
        axisZ = PointSet.axes[2]

        # any(PointSet.axes) should work as an emptiness check...
        # but it doesn't... dunno y =(
        if any(PointSet.axes[0]):
            if (not (bounds[0][0] < axisX[0] or bounds[0][1] > axisX[-1] or
                     bounds[1][0] < axisY[0] or bounds[1][1] > axisY[-1] or
                     bounds[2][0] < axisZ[0] or bounds[2][1] > axisY[-1])):
                vprint('No space extension needed')
                return False
            else:
                vprint('Extending axes')
                for i in (0, 1, 2):
                    bounds[i][0] = min(bounds[i][0], PointSet.axes[i][0])
                    bounds[i][1] = max(bounds[i][1], PointSet.axes[i][-1])

        PointSet.bounds = bounds
        intervals = (
            bounds[0][1] - bounds[0][0],
            bounds[1][1] - bounds[1][0],
            bounds[2][1] - bounds[2][0]
        )

        PointSet.DELTA = min(intervals) / float(PointSet.RESOLUTION)

        # small constant for arange skew
        c = min(intervals) * 0.01
        PointSet.axes = (
            np.arange(bounds[0][0] - c, bounds[0][1] + c, PointSet.DELTA),
            np.arange(bounds[1][0] - c, bounds[1][1] + c, PointSet.DELTA),
            np.arange(bounds[2][0] - c, bounds[2][1] + c, PointSet.DELTA),
        )

        vprint("Space expanded with new parameters:")
        PointSet.printBounds()
        return True

    # STATUS MONITORING ###
    @classmethod
    def printBounds(cls):
        bounds = PointSet.bounds

        for i, W in enumerate('XYZ'):
            vprint("{} axis [start, end, length]:\n\t{}\t{}\t{}\t".format(
                W, bounds[i][0], bounds[i][1], len(PointSet.axes[i])))

    def printOpts(self):
        vprint('\tOptions for this set:\t')
        vprint('\tBINNING STEPS:\t{}'.format(self.BINSTEPS))
        vprint('\tDENS RADIUS:\t{}'.format(self.DENSITY_RADIUS))
        vprint('\tRESOLUTION:\t{}'.format(PointSet.RESOLUTION))

    def coarseErr(self):
        vprint('\nProblem: grid is too coarse, increment resolution!!')
        exit('coarse error')

    # MAIN CALCULATION FUNCTIONS ###

    def setSampleDensity(self):
        # SAMPLE DENSITY IS COPIED FOR EACH POINT IN SET
        vprint("Constructing new Sample density... ")

        R = self.DENSITY_RADIUS

        def evalDens(x, y, z):
            return max(gf.dens(R, gf.norm([x, y, z])), 0)
        # localMesh ##
        side = np.arange(-R, R, PointSet.DELTA)
        mX, mY, mZ = np.meshgrid(side, side, side)
        try:
            self.sampleTens = np.vectorize(
                evalDens)(mX, mY, mZ)[1:-1, 1:-1, 1:-1]
        except IndexError:
            self.coarseErr()
            raise
        if np.count_nonzero(self.sampleTens > 0) < 5:
            self.coarseErr()

        vprint("\bDone")

    def getDensityTensor(self):
        if self.checkDimension():
            self.setDensityTensor()
        return self.D

    def getBinned(self):
        self.binterval = gf.getBinterval(self.D, self.BINSTEPS)

        def binVal(x):
            return self.interval[gf.findNearest(self.binterval, x)]

        return np.vectorize(binVal)(self.D)

    def getBinnedVolumes(self):
        self.binterval = gf.getBinterval(self.D, self.BINSTEPS)
        if self.binVols:
            return self.binVols
        for binStep in self.binterval:
            self.binVols.append(
                np.count_nonzero(self.D > binStep) * PointSet.DELTA)
        return self.binVols

    def setDensityTensor(self):
        if verbose:
            v.printHeader('Calculating density tensor for ' + self.IN_FILE)
        self.printOpts()
        self.setSampleDensity()
        self.read3DPoints()

        axesLen = np.vectorize(len)(PointSet.axes)
        vprint('Allocating memory, total: {} entries'.format(
            np.prod(axesLen)))
        self.D = np.zeros(axesLen, dtype=np.float)
        vprint("Calculating density tensor")
        if verbose:
            bar = v.StatusBar(len(self.pointList))
        for P in self.pointList:
            if verbose:
                bar.update()
            # top left coordinates ###
            C = (P[0] - self.DENSITY_RADIUS,
                 P[1] - self.DENSITY_RADIUS,
                 P[2] - self.DENSITY_RADIUS)

            xFrom = findNearestIndex(PointSet.axes[0], C[0])
            yFrom = findNearestIndex(PointSet.axes[1], C[1])
            zFrom = findNearestIndex(PointSet.axes[2], C[2])
            xTo = xFrom + self.sampleTens.shape[0]
            yTo = yFrom + self.sampleTens.shape[1]
            zTo = zFrom + self.sampleTens.shape[2]

            try:
                self.D[xFrom:xTo, yFrom:yTo, zFrom:zTo] += self.sampleTens
            except ValueError:
                self.coarseErr()
                self.printBounds()
                raise
