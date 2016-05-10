import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys
import os

# OWN MODULES#
import promptParser
import Visualizer as v
import globalFunctions


findNearest = globalFunctions.findNearest
dist = globalFunctions.dist

np.set_printoptions(precision=2)


class dataSet:

    def __init__(self, D, I, T):
        # METAPARAMETERS ###
        self.DENSITY_RADIUS = D
        self.IN_FILE = I
        self.TRESHOLD = T
        self.printArgs()
        try:
            self.IN = pd.read_csv(self.IN_FILE, delimiter='\t')
        except IOError as e:
            print e.message
            print 'Skipping this set...'
            raise

    # GLOBAL VARIABLES ###
    RESOLUTION = 0
    axY, axX = [], []
    sampleTens = []
    DELTA = 0
    TotalPoints = 0

    # I/O SUPPORT FUNCTIONS ###
    def read2DPoints(self):

        self.pointList = self.IN[['X', 'Y']].values
        dataSet.TotalPoints += len(self.pointList)
        print "Reading {} point finished, total count: {}".format(
            len(self.pointList), dataSet.TotalPoints)

    def checkDimension(self):
        edge = self.DENSITY_RADIUS
        print '\nChecking global dimensions...\n'
        self.extend2Dimensions(
            self.IN.X.min() - edge,
            self.IN.X.max() + edge,
            self.IN.Y.min() - edge,
            self.IN.Y.max() + edge
        )

    def extend2Dimensions(self, xMin, xMax, yMin, yMax):
        axX = dataSet.axX
        axY = dataSet.axY

        if not (len(dataSet.axX) == 0 or len(dataSet.axY) == 0):
            if (not (xMin < axX[0] or xMax > axX[-1] or
                     yMin < axY[0] or yMax > axY[-1])):
                print 'No space extension needed'
                return
            else:
                xMin = min(xMin, axX[0])
                xMax = max(xMax, axX[-1])
                yMin = min(yMin, axY[0])
                yMax = max(yMax, axY[-1])

        print 'Extending axes'

        intervals = (
            xMax - xMin,
            yMax - yMin
        )
        if intervals[0] == min(intervals):
            dataSet.DELTA = intervals[0] / float(dataSet.RESOLUTION)
        elif intervals[1] == min(intervals):
            dataSet.DELTA = intervals[1] / float(dataSet.RESOLUTION)

        # 0.01 constant for arange skew
        dataSet.axX = np.arange(xMin, xMax, dataSet.DELTA)
        dataSet.axY = np.arange(yMin, yMax, dataSet.DELTA)

        print "Space expanded with new parameters:"
        print "X axis [start, end, length]:\n\t{}\t{}\t{}\t".format(
            dataSet.axX[0], dataSet.axX[-1], len(dataSet.axX))
        print "Y axis [start, end, length]:\n\t{}\t{}\t{}\n\n".format(
            dataSet.axY[0], dataSet.axY[-1], len(dataSet.axY))

    # STATUS MONITORING ###
    def printArgs(self):
        v.printHeader("\nReading in file:\t" + self.IN_FILE)
        print '\tOptions for this set:\t'
        print '\tTRESHOLD:\t{}'.format(self.TRESHOLD)
        print '\tDENS RADIUS:\t{}'.format(self.DENSITY_RADIUS)
        print '\tRESOLUTION:\t{}'.format(dataSet.RESOLUTION)

    def coarseErr(self):
        print "\nProblem: grid is too coarse, increment resolution!!"
        exit(1)

    # MAIN CALCULATION FUNCTIONS ###

    def dens(self, r):
        return self.DENSITY_RADIUS - r

    def setSampleDensity(self):
        print "Constructing new Sample density... ",

        def evalDens(x, y):
            return max(self.dens(dist([x, y], [0, 0])), 0)
        # localMesh ##
        r = self.DENSITY_RADIUS
        side = np.arange(-r, r, dataSet.DELTA)

        mX, mY = np.meshgrid(side, side)
        try:
            dataSet.sampleTens = np.vectorize(evalDens)(mX, mY)[1:-1, 1:-1]
        except IndexError:
            self.coarseErr()
        if np.count_nonzero(dataSet.sampleTens > 0) < 5:
            self.coarseErr()

        print "Done"

    def getDensityTensor(self):

        v.printHeader('Calculating density tensor for ' + self.IN_FILE)
        self.setSampleDensity()
        self.read2DPoints()

        axX = dataSet.axX
        axY = dataSet.axY
        ST = dataSet.sampleTens
        print 'Allocating memory, total: {} entries'.format(
            len(axX) * len(axY))
        self.D = np.zeros((len(axY), len(axX)), dtype=np.float)
        print "Calculating density tensor"
        bar = v.StatusBar(len(self.pointList))
        for P in self.pointList:
            bar.incrementStatusBar()
            # top left coordinates ###
            C = (P[0] - self.DENSITY_RADIUS,
                 P[1] - self.DENSITY_RADIUS)
            xFrom = findNearest(axX, C[0])
            yFrom = findNearest(axY, C[1])
            xTo = xFrom + ST.shape[1]
            yTo = yFrom + ST.shape[0]

            try:
                self.D[yFrom:yTo, xFrom:xTo] += ST
            except ValueError:
                self.coarseErr()

        return self.D

# RUNNING CODE


def main():

    args = promptParser.args
    dataSet.RESOLUTION = args.res

    sets = []

    v.printHeader(
        'Starting process, total samples: {}'.format(len(args.inputs)))

    for i in xrange(len(args.inputs)):
        ds = dataSet(args.rad[i], args.inputs[i], args.thd[i])
        ds.checkDimension()
        sets.append(ds)

    axX = dataSet.axX
    axY = dataSet.axY

    DMap = np.zeros((len(axY), len(axX)), dtype=np.float)
    for ds in sets:
        DMap += ds.getDensityTensor()

    v.printHeader('Rendering output...')

    if args.output is not None:
        globalFunctions.ensure_dir(args.output[0])

    for i, ds in enumerate(sets):

        head, tail = os.path.split(ds.IN_FILE)
        tail, ext = os.path.splitext(tail)
        if args.output is not None:
            head = args.output[0]

        OUT_FILE = os.path.normpath(head + '/' + tail)

        OUT_NAME = '{}-r{}-b{}-t{}.png'.format(OUT_FILE,
                                               ds.DENSITY_RADIUS,
                                               args.binn[i],
                                               ds.TRESHOLD)
        print ('Saving file: ' + OUT_NAME)
        v.TensorReader(ds).getFigure(args.binn[i]).savefig(OUT_NAME)

    v.printHeader('\nSuccess!')

if __name__ == "__main__":
    try:
        main()
    except:
        print 'Exiting with exception:', sys.exc_info()[1]
        raise
