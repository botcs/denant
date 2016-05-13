import argparse
import itertools

defRad = 1000
defThd = 1000
defRes = 50
defBin = 3

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
    type=int, default=[defBin],
    metavar='',
    help='Binning step (does *NOT* bin the measurement values)',
    dest='binn'
)

parser.add_argument(
    '-r', '--radius', nargs='+',
    help='Rad(s) of density sphere(s) for corresponding input(s)...',
    type=int, default=[defRad],
    metavar='',
    dest='rad'
)
parser.add_argument(
    '-t', '--treshold', nargs='+',
    help='Threshold sum of overlapping densities',
    type=int, default=[defThd],
    metavar='',
    dest='thd'
)

parser.add_argument(
    '-R', '--resolution',
    help='steps for SHORTEST axis (corresponding axes will be adjusted)',
    type=int, default=defRes,
    metavar='',
    dest='res')

parser.add_argument(
    '-o', '--output', nargs=1,
    help='Specify output directory (relative path from call)',
    default=['default_output'],
    metavar='')

parser.add_argument(
    '-c', '--cartesian',
    action='store_true',
    help='''Takes the cartesian product of the given option set
            and handles each productum as a sample.
            Evaluates to TRUE by default if only one input is
            specified with multiple options. If -c flag is not set
            for multiple input files, then options will be applied
            in respect of the input order, and will be extended by
            default values if there are more inputs than corresponding
            options''')

args = parser.parse_args()

if len(args.inputs) == 1 or args.cartesian:
    # make a Cartesian product of sample value pairs
    I, R, T, B = [], [], [], []
    for element in itertools.product(
            args.inputs, args.rad, args.thd, args.binn):
        I.append(element[0])
        R.append(element[1])
        T.append(element[2])
        B.append(element[3])
        args.inputs, args.rad, args.thd, args.binn = I, R, T, B
else:
    # extend default values for unspecified samples
    if len(args.rad) < len(args.inputs):
        args.rad.extend([defRad] * (len(args.inputs) - len(args.rad)))
    if len(args.thd) < len(args.inputs):
        args.thd.extend([defThd] * (len(args.inputs) - len(args.thd)))
    if len(args.binn) < len(args.inputs):
        args.binn.extend([defBin] * (len(args.inputs) - len(args.binn)))
