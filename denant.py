#!/usr/bin/env python
import numpy as np
import sys
# OWN MODULES#
import promptParser
import tensorplot as v
import globals
import denstensor as dt


np.set_printoptions(precision=2)


# RUNNING CODE
def main():
    globals.initFromPrompt()
    sets = []
    globals.ensure_dir(globals.output[0])

    print '\n\tStarting process, total samples: {}'.format(len(globals.inputs))

    for i in xrange(len(globals.inputs)):
        ds = dt.PointSet(globals.rad[i], globals.inputs[i], globals.binn[i])
        ds.checkDimension()
        sets.append(ds)

    v.printHeader('Calculating density tensors...')
    bar = v.StatusBar(len(sets))
    for ds in sets:
        ds.setDensityTensor()
        if not globals.verbose:
            bar.update()

    v.printHeader('Saving figures...')
    if globals.verbose:
        for i, ds in enumerate(sets):
            v.SingleTensorPlot(ds).savefig(globals.output[0], globals.separated)
        print ('\nSuccess!')
    else:
        job_count = 0
        for ds in sets:
            job_count += ds.BINSTEPS

        bar = v.StatusBar(job_count)
        for i, ds in enumerate(sets):
            v.SingleTensorPlot(ds).savefig(
                globals.output[0], globals.separated, bar)


if __name__ == "__main__":
    try:
        main()
    except:
        print 'Exiting with exception:', sys.exc_info()[1]
        raise
