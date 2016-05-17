#!/usr/bin/env python
import numpy as np
import sys
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
    globalFunctions.ensure_dir(args.output[0])

    print '\n\tStarting process, total samples: {}'.format(len(args.inputs))

    for i in xrange(len(args.inputs)):
        ds = dt.PointSet(args.rad[i], args.inputs[i], args.binn[i])
        ds.checkDimension()
        sets.append(ds)

    v.printHeader('Calculating density tensors...')
    bar = v.StatusBar(len(sets))
    for ds in sets:
        ds.setDensityTensor()
        if not args.verbose:
            bar.update()

    v.printHeader('Saving figures...')
    if args.verbose:
        for i, ds in enumerate(sets):
            v.TensorReader(ds).savefig(args.output[0], args.separated)
        print ('\nSuccess!')
    else:
        job_count = 0
        for ds in sets:
            job_count += ds.BINSTEPS

        bar = v.StatusBar(job_count)
        for i, ds in enumerate(sets):
            v.TensorReader(ds).savefig(
                args.output[0], args.separated, bar)


if __name__ == "__main__":
    try:
        main()
    except:
        print 'Exiting with exception:', sys.exc_info()[1]
        raise
