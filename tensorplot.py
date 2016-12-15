import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np
import globals
import denstensor
import os

findNearest = globals.findNearest


def forceAspect(ax, aspect=1):
    im = ax.get_images()
    extent = im[0].get_extent()
    ax.set_aspect(abs((extent[1] - extent[0]) /
                      (extent[3] - extent[2])) / aspect)


class VersusTensorPlot:
    """For plotting intersection of the two specified samples.
    ***IMPORTANT*** Only specified parameters are accepted, since the
    trial and error would not be an efficient workflow here
    """

    def __init__(self, dataset1, dataset2):
        self.ds1 = dataset1
        self.ds2 = dataset2
        #self.T1 = np.mean(self.ds1.D, axis=2)
        #self.T2 = np.mean(self.ds2.D, axis=2)
        self.T1 = self.ds1.D
        self.T2 = self.ds2.D

    def getFigure(self):

        axX = globals.axes[0]
        axY = globals.axes[1]
        axZ = globals.axes[2]
        
        cornersX = [axY[0], axY[-1], axZ[-1], axZ[0]]
        cornersY = [axX[0], axX[-1], axZ[-1], axZ[0]]        
        cornersZ = [axX[0], axX[-1], axY[-1], axY[0]]

        plt.close()
        fig = plt.figure(figsize=(16, 9))
        
    
        ISTensor = np.zeros(self.T1.shape, dtype=int)
        '''TURNING BOOLEAN ARRAY TO INT ARRAY'''
        ISTensor += -100 * (self.T1 > globals.versus[0])
        ISTensor += 101 * (self.T2 > globals.versus[1])
        
        intersectionMap = plt.subplot(231)
        intersectionMap.set_title('X projection')
        intersectionMap.imshow(
            ISTensor.sum(axis=0),
            cmap=plt.cm.gray,
            interpolation='None',
            #aspect=1, 
            extent=cornersX)
        intersectionMap.locator_params(nbins=4)


        intersectionMap = plt.subplot(232)
        intersectionMap.set_title('Y projection')
        intersectionMap.imshow(
            ISTensor.sum(axis=1),
            cmap=plt.cm.gray,
            interpolation='None',
            #aspect=1, 
            extent=cornersY)
        intersectionMap.locator_params(nbins=4)


        intersectionMap = plt.subplot(233)
        intersectionMap.set_title('Z projection')
        intersectionMap.imshow(
            ISTensor.sum(axis=2),
            cmap=plt.cm.gray,
            interpolation='None',
            #aspect=1, 
            extent=cornersZ)
        intersectionMap.locator_params(nbins=4)


        ax = plt.subplot(235)
        title = '{} treshold:{}\n{} treshold:{}\nThresholded volume: {}'.format(
            self.ds1.name, globals.versus[0],
            self.ds2.name, globals.versus[1],
            denstensor.getTresholdedVolumeMeasure((ISTensor==1)*2, 1))
        ax.set_title(title)
        ax.imshow(
            ((ISTensor==1)*1).sum(axis=2),
            cmap=plt.cm.gray,
#            aspect=1,
            interpolation='None',
            extent=cornersZ)
            
        ax.locator_params(nbins=4)

        plt.tight_layout()

        return fig

    def savefig(self, output_dir):

        OUT_NAME = '{}/{}-VS-{}-treshold-{}-{}.png'.format(
            output_dir,
            self.ds1.name,
            self.ds2.name,
            globals.versus[0],
            globals.versus[1])

        print('Saving...  ' + OUT_NAME)
        self.getFigure().savefig(OUT_NAME)


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
        self.T = np.mean(self.ds.D, axis=2)
        #self.T = self.ds.D[:,:,self.ds.D.shape[2]/2]
        #self.T = np.sum(self.ds.D, axis=2)
        self.T = self.T.transpose()

    def savefig(self, output_dir, separated=None, bar=None):

        if separated:
            separated_dir = '{}/{}'.format(
                output_dir,
                self.ds.name)
            globals.ensure_dir(separated_dir)

            for step in range(self.ds.BINSTEPS):
                OUT_NAME = '{}/{}-step{}.png'.format(
                    separated_dir, self.ds.name, step)
                self.getSeparatedFigure(step).savefig(OUT_NAME)
                globals.printVerbose('\t' + os.path.split(OUT_NAME)[1])
                if bar:
                    bar.update()

        else:
            OUT_NAME = '{}/{}.png'.format(
                output_dir, self.ds.name)

            globals.printVerbose('Saving...  ' + OUT_NAME)
            self.getSingleFigure(bar).savefig(OUT_NAME)
            # plt.show()

    def getSeparatedFigure(self, step):
        axX = globals.axes[0]
        axY = globals.axes[1]
        corners = [axX[0], axX[-1], axY[-1], axY[0]]
        vols = self.ds.getBinVols()

        plt.close()
        fig = plt.gcf()
        fig.suptitle(self.ds.IN_FILE, fontsize=14, fontweight='bold')

        mainMap = plt.subplot(121)
        mainMap.set_title('Density map,\nRadius: {}\nBinning steps: {}'.format(
            self.ds.DENSITY_RADIUS, self.ds.BINSTEPS))
        mainMap.imshow(
            self.getBinned(self.ds.BINSTEPS), cmap=plt.cm.gray,
            interpolation='None', extent=corners, aspect=1)
        mainMap.locator_params(nbins=4)

        ax = plt.subplot(122)
        title = 'Step: {}\nTreshold value: {}\nThresholded volume: {}'.format(
            step, self.ds.binterval[step], vols[step])
        ax.set_title(title)
        ax.imshow(
            self.T > self.binterval[step],
            cmap=plt.cm.gray,
            aspect=1,
            interpolation='None',
            extent=corners)
        ax.locator_params(nbins=4)

        fig.set_size_inches(10, 6)
        plt.tight_layout()

        return fig

    def getSingleFigure(self, bar=None):
        axX = globals.axes[0]
        axY = globals.axes[1]
        corners = [axX[0], axX[-1], axY[-1], axY[0]]
        vols = self.ds.getBinVols()
        colnum = 3
        gridShape = [(self.ds.BINSTEPS / colnum) + 1, colnum]
        if (self.ds.BINSTEPS) % colnum > 0:
            gridShape[0] += 1

        plt.close()
        fig = plt.gcf()
        fig.suptitle(self.ds.name, fontsize=14, fontweight='bold')

        mainMap = plt.subplot2grid(
            gridShape, (0, colnum / 2))
        mainMap.set_title('Density map,\nRadius: {}\nBinning steps: {}'.format(
            self.ds.DENSITY_RADIUS, self.ds.BINSTEPS))

        mainMap.imshow(
            self.getBinned(self.ds.BINSTEPS), cmap=plt.cm.gray,
            interpolation='None',
            aspect=1,
            extent=corners
        )
        # forceAspect(mainMap)
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
                interpolation='None',
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
        TSum = np.zeros(self.T.shape)
        for b in self.binterval:
            TSum += self.T > b
        return TSum
