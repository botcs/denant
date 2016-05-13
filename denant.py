#!/usr/bin/env python
import numpy as np
import sys
import os

# OWN MODULES#
import promptParser
import Visualizer as v
import globalFunctions
import denstensor as dt
np.set_printoptions(precision=2)


# RUNNING CODE
def main():
    args = promptParser.args
    dt.PointSet.RESOLUTION = args.res

    sets = []

    print '\n\tStarting process, total samples: {}'.format(len(args.inputs))

    for i in xrange(len(args.inputs)):
        ds = dt.PointSet(args.rad[i], args.inputs[i], args.thd[i])
        ds.checkDimension()
        sets.append(ds)

    v.printHeader('Calculating density tensors...')
    bar = v.StatusBar(len(sets))
    for ds in sets:
        ds.setDensityTensor()
        if not args.verbose:
            bar.incrementStatusBar()

    globalFunctions.ensure_dir(args.output[0])

    v.printHeader('Saving files...')
    bar = v.StatusBar(len(sets))
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

        v.TensorReader(ds).getFigure(args.binn[i]).savefig(OUT_NAME)

        if args.verbose:
            print (OUT_NAME)
        else:
            bar.incrementStatusBar()

    if args.verbose:
        print ('\nSuccess!')

if __name__ == "__main__":
    try:
        main()
    except:
        print 'Exiting with exception:', sys.exc_info()[1]
        raise
