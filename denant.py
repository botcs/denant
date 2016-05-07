import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import argparse
import sys

np.set_printoptions(precision=2)


def dist(p1, p2):
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def findNearest(array, value):
    idx = np.searchsorted(array, value, side="left")
    if idx == len(array) or \
       np.abs(value - array[idx - 1]) < np.abs(value - array[idx]):
        return idx - 1
    else:
        return idx


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
    densTens = []
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
        print "\nReading in file:\t" + self.IN_FILE
        print 45 * '-'
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
            dataSet.densTens = np.vectorize(evalDens)(mX, mY)[1:-1, 1:-1]
        except IndexError:
            self.coarseErr()
        if np.count_nonzero(dataSet.densTens > 0) < 5:
            self.coarseErr()

        print "Done"

    def getDensity(self):

        print 'Calculating density tensor for ' + self.IN_FILE
        print 45 * '-'
        self.setSampleDensity()
        self.read2DPoints()

        axX = dataSet.axX
        axY = dataSet.axY
        densTens = dataSet.densTens
        print 'Allocating memory, total: {} entries'.format(
            len(axX) * len(axY))
        self.D = np.zeros((len(axY), len(axX)), dtype=np.float)
        print "Calculating density tensor"
        bar = StatusBar(len(self.pointList))
        for P in self.pointList:
            bar.incrementStatusBar()
            # top left coordinates ###
            C = (P[0] - self.DENSITY_RADIUS,
                 P[1] - self.DENSITY_RADIUS)
            xFrom = findNearest(axX, C[0])
            yFrom = findNearest(axY, C[1])
            xTo = xFrom + densTens.shape[1]
            yTo = yFrom + densTens.shape[0]

            try:
                self.D[yFrom:yTo, xFrom:xTo] += densTens
            except ValueError:
                self.coarseErr()

        return self.D


class StatusBar:

    def __init__(self, total, barLength=30):
        self.total = total
        self.curr = 0
        self.percentage = 0
        self.barLength = barLength

    def barStr(self):
        currBar = self.barLength * self.percentage / 100
        return '[' + "=" * currBar + " " * (self.barLength - currBar) + ']'

    def printStatusBar(self):
        print("\r  " + self.barStr() + "  Done/Total (" +
              str(self.curr) + '/' + str(self.total) + ")   " +
              str(100 * self.curr / self.total) + "%     "),
        sys.stdout.flush()
        if(self.percentage == 100):
            print '\n\tfinished\n'

    def incrementStatusBar(self):
        self.curr += 1
        self.updateStatusBar()

    def updateStatusBar(self):
        currPercentage = self.curr * 100 / self.total
        if(currPercentage > self.percentage):
            self.percentage = currPercentage
            self.printStatusBar()


def treshHold(densTensor, limit):
    return densTensor > limit

# RUNNING CODE


def main():

    defRad = 1000
    defThd = 1000
    defRes = 300

    parser = argparse.ArgumentParser(
        description='''DENANT: Densitiy Analysis Tool for 3D
        points overlap statistics''',
        usage='''denant.py <input file(s)...> [OPTIONS] <args>''',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        '-v', '--version',
        action='version',
        version='DenAnT BETA - botcs'
    )
    parser.add_argument(
        'inputs', nargs='+',
        default='in.txt',
        #        type=argparse.FileType('r'),
        help='Input csv file(s)...',
    )
    parser.add_argument(
        '-r', '--radius', nargs='+',
        help='Rad(s) of density sphere(s) for corresponding input(s)...',
        type=int, default=[defRad],
        dest='rad'
    )
    parser.add_argument(
        '-t', '--treshold', nargs='+',
        help='Threshold sum of overlapping densities',
        type=int, default=[defThd],
        dest='thd'
    )

    parser.add_argument(
        '-R', '--resolution',
        help='spacing for SHORTEST axis (corresponding axes will be adjusted)',
        type=int, default=defRes,
        dest='res'
    )

    args = parser.parse_args()

    dataSet.RESOLUTION = args.res
    sets = []
    if len(args.rad) < len(args.inputs):
        args.rad.extend([defRad] * (len(args.inputs) - len(args.rad)))

    if len(args.thd) < len(args.inputs):
        args.thd.extend([defThd] * (len(args.inputs) - len(args.thd)))

    for i in xrange(len(args.inputs)):
        ds = dataSet(args.rad[i], args.inputs[i], args.thd[i])

        ds.checkDimension()
        sets.append(ds)

    axX = dataSet.axX
    axY = dataSet.axY

    DMap = np.zeros((len(axY), len(axX)), dtype=np.float)
    for ds in sets:
        DMap += ds.getDensity()

    plt.figure(1)
    plt.subplot(121)
    plt.imshow(DMap, cmap=plt.cm.gray,
               interpolation="none", extent=[axX[0], axX[-1], axY[-1], axY[0]])
    plt.subplot(122)
    plt.imshow(DMap > args.thd[0],
               cmap=plt.cm.gray, interpolation="none",
               extent=[axX[0], axX[-1], axX[-1], axY[0]])
    plt.show()


if __name__ == "__main__":
    try:
        main()
    except:
        print 'Exiting with exception:', sys.exc_info()[1]
        raise
