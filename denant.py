#!/usr/bin/env python
import numpy as np
import sys
# OWN MODULES#
import promptParser
import tensorplot as tplt
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

    globals.printHeader('Calculating density tensors...')
    bar = globals.StatusBar(len(sets))
    for ds in sets:
        ds.setDensityTensor()
        if not globals.verbose:
            bar.update()

    globals.printHeader('Saving figures...')
    if globals.versus:
        versusMode(sets)
    else:
        singleMode(sets)
def versusMode(sets):
    tplt.VersusTensorPlot(sets[0], sets[1]).savefig(globals.output)
    
    
def singleMode(sets):
    if globals.verbose:
        for i, ds in enumerate(sets):
            tplt.SingleTensorPlot(ds).savefig(globals.output, globals.separated)
        print ('\nSuccess!')
    else:
        job_count = 0
        for ds in sets:
            job_count += ds.BINSTEPS

        bar = globals.StatusBar(job_count)
        for i, ds in enumerate(sets):
            tplt.SingleTensorPlot(ds).savefig(
                globals.output[0], globals.separated, bar)

    
if __name__ == "__main__":
    try:
        main()
    except:
        print 'Exiting with exception:', sys.exc_info()[1]
        raise
