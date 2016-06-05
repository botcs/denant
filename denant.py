#!/usr/bin/env python
import numpy as np
import sys
# OWN MODULES#
import tensorplot as tplt
import globals
import denstensor as dt


np.set_printoptions(precision=2)


# RUNNING CODE
def main():
    globals.initFromPrompt()
    sets = []
    step = 0

    globals.printHeader(
        '  Starting process, total samples: {}'.format(len(globals.inputs)))

    for i in xrange(len(globals.inputs)):
        ds = dt.PointSet(globals.rad[i], globals.binn[i], globals.inputs[i])
        sets.append(ds)
    globals.printVerbose(
        'Reading {} files finished, total points: {}'.format(
            len(globals.inputs), globals.TotalPoints))

    if globals.verbose:
        globals.printHeader('  Setting global dimensions (0/0)')
    for ds in sets:
        ds.checkDimension()

    step += 1
    globals.printHeader('  Calculating density tensors ({}/2)'.format(step))
    bar = globals.StatusBar(len(sets))
    for ds in sets:
        ds.setDensityTensor()
        if not globals.verbose:
            bar.update()

    step += 1
    globals.printHeader('  Saving figures ({}/2)'.format(step))
    globals.ensure_dir(globals.output)
    if globals.versus:
        versusMode(sets)
    else:
        singleMode(sets)


def versusMode(sets):
    tplt.VersusTensorPlot(sets[0], sets[1]).savefig(globals.output)


def singleMode(sets):
    if globals.verbose:
        for i, ds in enumerate(sets):
            tplt.SingleTensorPlot(ds).savefig(
                globals.output, globals.separated)
        print ('\nSuccess!')
    else:
        job_count = 0
        for ds in sets:
            job_count += ds.BINSTEPS

        bar = globals.StatusBar(job_count)
        for i, ds in enumerate(sets):
            tplt.SingleTensorPlot(ds).savefig(
                globals.output, globals.separated, bar)


if __name__ == "__main__":
    try:
        main()
    except:
        print 'Exiting with exception:', sys.exc_info()[1]
        raise
