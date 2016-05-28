import matplotlib.pyplot as plt
import numpy as np
import sys
import globals as globals
import os

findNearest = globals.findNearest


def printHeader(h):

    hBar = len(h) * '-'
    print '\n' + hBar
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

def forceAspect(ax,aspect=1):
    im = ax.get_images()
    extent =  im[0].get_extent()
    ax.set_aspect(abs((extent[1]-extent[0])/(extent[3]-extent[2]))/aspect)

class VersusTensorPlot:
    """For plotting intersection of the two specified samples.
    ***IMPORTANT*** Only specified parameters are accepted, since the
    trial and error would not be an efficient workflow here
    """
    
    def __init__(self, dataset1, dataset2):
        self.ds1 = dataset1
        self.ds2 = dataset2
        self.T1 = np.sum(self.ds1.D, axis=2)
        self.T2 = np.sum(self.ds2.D, axis=2)

    def getFigure(self, step):
        axX = globals.axes[0]
        axY = globals.axes[1]
        corners = [axX[0], axX[-1], axY[-1], axY[0]]
        vols = self.ds.getBinnedVolumes()

        plt.close()
        fig = plt.gcf()
        fig.suptitle(self.ds.IN_FILE, fontsize=14, fontweight='bold')

        mainMap = plt.subplot(121)
        mainMap.set_title('Density map,\nRadius: {}\nBinning steps: {}'.format(
            self.ds.DENSITY_RADIUS, self.ds.BINSTEPS))
        mainMap.imshow(
            self.getBinned(self.ds.BINSTEPS), cmap=plt.cm.gray,
            interpolation=None, extent=corners, aspect=1)
        mainMap.locator_params(nbins=4)

        ax = plt.subplot(122)
        title = 'Step: {}\nTreshold value: {}\nThresholded volume: {}'.format(
            step, self.ds.binterval[step], vols[step])
        ax.set_title(title)
        ax.imshow(
            self.T > self.binterval[step],
            cmap=plt.cm.gray,
            aspect=1,
            interpolation=None, extent=corners)
        ax.locator_params(nbins=4)

        fig.set_size_inches(10, 6)
        plt.tight_layout()

        return fig


        
            
            
class SingleTensorPlot:
    '''For visualising single density tensor's plot with the corresponding
    treshold, binning value and the tresholded space's volume Two
    possible output:

    single map: the actual binning map is the top picture and the
    pictures beneath are representing the tresholded volumes
    
    separated map: figure is generated for each binning step in sample
    with the full map on the left and the actual tresholded volume on
    the right

    '''
    def __init__(self, dataset):
        self.ds = dataset
        '''Visualize default: mean of values on axis Z'''
        #self.T = np.mean(self.ds.D, axis=2)
        #self.T = self.ds.D[:,:,24]
        self.T = np.sum(self.ds.D, axis=2)
        self.T = self.T.transpose()

    def savefig(self, output_dir, separated=None, bar=None):
        head, tail = os.path.split(self.ds.IN_FILE)
        tail, ext = os.path.splitext(tail)
        OUT_PATH = os.path.normpath(output_dir + '/' + tail)

        if separated:
            separated_dir = '{}-radius{}-bin{}'.format(
                OUT_PATH, self.ds.DENSITY_RADIUS, self.ds.BINSTEPS)
            globals.ensure_dir(separated_dir)

            for step in range(self.ds.BINSTEPS):
                file_name = os.path.normpath(separated_dir + '/' + tail)
                OUT_NAME = '{}-radius{}-step{}.png'.format(
                    file_name, self.ds.DENSITY_RADIUS, step)
                self.getSeparatedFigure(step).savefig(OUT_NAME)
                globals.printVerbose('\t' + os.path.split(OUT_NAME)[1])
                if bar:
                    bar.update()

        else:
            OUT_NAME = '{}-radius{}-bin{}.png'.format(
                OUT_PATH, self.ds.DENSITY_RADIUS, self.ds.BINSTEPS)

            globals.printVerbose(OUT_NAME)
            self.getSingleFigure(bar).savefig(OUT_NAME)
            #plt.show()

    def getSeparatedFigure(self, step):
        axX = globals.axes[0]
        axY = globals.axes[1]
        corners = [axX[0], axX[-1], axY[-1], axY[0]]
        vols = self.ds.getBinnedVolumes()

        plt.close()
        fig = plt.gcf()
        fig.suptitle(self.ds.IN_FILE, fontsize=14, fontweight='bold')

        mainMap = plt.subplot(121)
        mainMap.set_title('Density map,\nRadius: {}\nBinning steps: {}'.format(
            self.ds.DENSITY_RADIUS, self.ds.BINSTEPS))
        mainMap.imshow(
            self.getBinned(self.ds.BINSTEPS), cmap=plt.cm.gray,
            interpolation=None, extent=corners, aspect=1)
        mainMap.locator_params(nbins=4)

        ax = plt.subplot(122)
        title = 'Step: {}\nTreshold value: {}\nThresholded volume: {}'.format(
            step, self.ds.binterval[step], vols[step])
        ax.set_title(title)
        ax.imshow(
            self.T > self.binterval[step],
            cmap=plt.cm.gray,
            aspect=1,
            interpolation=None, extent=corners)
        ax.locator_params(nbins=4)

        fig.set_size_inches(10, 6)
        plt.tight_layout()

        return fig

    def getSingleFigure(self, bar=None):
        axX = globals.axes[0]
        axY = globals.axes[1]
        corners = [axX[0], axX[-1], axY[-1], axY[0]]
        vols = self.ds.getBinnedVolumes()
        colnum = 3
        gridShape = [(self.ds.BINSTEPS / colnum) + 1, colnum]
        if (self.ds.BINSTEPS) % colnum > 0:
            gridShape[0] += 1

        plt.close()
        fig = plt.gcf()
        fig.suptitle(self.ds.IN_FILE, fontsize=14, fontweight='bold')

        mainMap = plt.subplot2grid(
            gridShape, (0, colnum / 2))
        mainMap.set_title('Density map,\nRadius: {}\nBinning steps: {}'.format(
            self.ds.DENSITY_RADIUS, self.ds.BINSTEPS))
        mainMap.imshow(
            self.getBinned(self.ds.BINSTEPS), cmap=plt.cm.gray,
            interpolation=None,
            aspect=1,
            extent=corners
        )
        #forceAspect(mainMap)
        mainMap.locator_params(nbins=4)

        plt.tight_layout()

        for step in range(self.ds.BINSTEPS):
            rowIndex = 1 + (step / colnum)
            colIndex = (step % colnum)
            # print '!!!!{}'.format(step)
            # print gridShape
            # print (rowIndex, colIndex)

            ax = plt.subplot2grid(gridShape, (rowIndex, colIndex))
            title = 'Step: {}\nTreshold value: {}\nThresholded volume: {}'.format(
                step, self.ds.binterval[step], vols[step])

            ax.set_title(title)
            ax.imshow(
                self.T > self.binterval[step],
                cmap=plt.cm.gray,
                aspect=1,
                interpolation=None,
                extent=corners
            )
            ax.locator_params(nbins=4)
            if bar:
                bar.update()

        fig.set_size_inches(colnum * 9, gridShape[0] * 8)
        fig.set_dpi(110)
        return fig

    def getBinned(self, steps):
        self.binterval = globals.getBinterval(self.T, self.ds.BINSTEPS)
        TSum = np.zeros(self.T.shape, dtype=bool)
        for b in self.binterval:
            TSum += self.T > b
        return TSum
