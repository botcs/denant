import matplotlib.pyplot as plt
import numpy as np
import sys
import globalFunctions

findNearest = globalFunctions.findNearest

hBar = 45 * '-' + '\n'


def printHeader(h):
    print h
    print hBar


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


class TensorReader:

    def __init__(self, dataset):
        self.ds = dataset
        self.T = dataset.D

    def getFigure(self, nbins=3):
        axX = self.ds.axX
        axY = self.ds.axY
        corners = [axX[0], axX[-1], axY[-1], axY[0]]

        plt.clf()
        f = plt.figure(1)
        f.suptitle(self.ds.IN_FILE, fontsize=14, fontweight='bold')
        plt.subplot(131)
        plt.title('Density Map\nradius: {}'.format(self.ds.DENSITY_RADIUS))
        plt.imshow(
            self.T, cmap=plt.cm.gray,
            interpolation="none", extent=corners)
        plt.locator_params(nbins=4)

        plt.subplot(132)
        plt.title('Binned Map\nsteps: {}'.format(nbins))
        plt.imshow(
            self.getBinned(nbins), cmap=plt.cm.gray,
            interpolation="none", extent=corners)
        plt.locator_params(nbins=4)

        plt.subplot(133)
        plt.title('Thresholded Map\nTreshold:{}'.format(self.ds.TRESHOLD))
        plt.imshow(
            self.T > self.ds.TRESHOLD, cmap=plt.cm.gray,
            interpolation="none", extent=corners)
        plt.locator_params(nbins=4)

        f.set_size_inches(18.5, 8)
        return f

    def getBinned(self, steps):
        maxVal = np.max(self.T)
        minVal = np.min(self.T)
        self.interval = np.linspace(minVal, maxVal + 0.001, steps)

        def binVal(x):
            return self.interval[findNearest(self.interval, x)]

        return np.vectorize(binVal)(self.T)
