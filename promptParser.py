import argparse
import itertools
import globals


parser = argparse.ArgumentParser(
    description='''DENANT: Densitiy Analysis Tool for 3D
    points overlap statistics''',
    usage='''denant.py <input file(s)...> [OPTIONS] <args>''',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)

parser.add_argument(
    '-v', '--verbose',
    action='store_true',
    help='Flag for printing detailed informations about process steps'
)
parser.add_argument(
    '--version',
    action='version',
    version='DenAnT BETA - botcs'
)
parser.add_argument(
    'inputs', nargs='+',
    default='in.txt',
    metavar='',
    help='Input csv file(s)...',
)
parser.add_argument(
    '-b', '--binning', nargs='+',
    type=int, default=globals.binn,
    metavar='',
    help='Binning step (does *NOT* bin the measurement values)',
    dest='binn'
)

parser.add_argument(
    '-r', '--radius', nargs='+',
    help='Rad(s) of density sphere(s) for corresponding input(s)...',
    type=int, default=globals.rad,
    metavar='',
    dest='rad'
)

parser.add_argument(
    '-R', '--resolution',
    help='steps for SHORTEST axis (corresponding axes will be adjusted)',
    type=int, default=globals.res,
    metavar='',
    dest='res')

parser.add_argument(
    '-o', '--output', nargs=1,
    help='Specify output directory (relative path from call)',
    default=[globals.output],
    metavar='')

parser.add_argument(
    '-c', '--cartesian',
    action='store_true',
    help='''Takes the cartesian product of the given option set
            and handles each productum as an individual input argument.
            Evaluates to TRUE by default if only ONE input is
            specified with multiple options. If -c flag is not set
            for multiple input files, then options will be applied
            in respect of the input order, and will be extended by
            default values if there are more inputs than corresponding
            options''')

parser.add_argument(
    '-s', '--separated',
    action='store_true',
    help='Save output images into separate subfolders of output folder')


parser.add_argument(
    '-vs', '--versus',
    nargs=2,
    help='''VERSUS MODE: In this mode only two inputs are accepted with the
            corresponding threshold values. Specify threshold values after the
            -vs flag.
            
            NOTE: In VERSUS mode the -c -s -b options are discarded.
            ''',
    type=int,
    metavar=''
)

def reshapeInput(args):
    
    '''Completing the user input if necessary'''

    if args.versus and len(args.inputs) != 2:
        exit('VERSUS MODE ERROR: Wrong number of inputs: ' +
             str(len(args.inputs)))

    if len(args.inputs) == 1:
        args.cartesian = True

    if args.cartesian:
        '''make a Cartesian product of sample value pairs'''
        I, R, B = [], [], []
        for element in itertools.product(args.inputs, args.rad, args.binn):
            I.append(element[0])
            R.append(element[1])
            B.append(element[2])
        args.inputs, args.rad, args.binn = I, R, B
    else:
        '''extend default values for unspecified samples'''
        if len(args.rad) < len(args.inputs):
            args.rad.extend(globals.rad * (len(args.inputs) - len(args.rad)))

        if len(args.binn) < len(args.inputs):
            args.binn.extend(globals.binn * (len(args.inputs) -
                                                 len(args.binn)))


def parse(reshape=True):
    args = parser.parse_args()
    if reshape:
        reshapeInput(args)
    return args
