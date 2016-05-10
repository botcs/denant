import argparse
import itertools

defRad = 1000
defThd = 1000
defRes = 300
defBin = 3

parser = argparse.ArgumentParser(
    description='''DENANT: Densitiy Analysis Tool for 3D
    points overlap statistics''',
    usage='''denant.py <input file(s)...> [OPTIONS] <args>''',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)

parser.add_argument(
    '-v', '--version',
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
    metavar=''
)

args = parser.parse_args()


if len(args.inputs) > 1:
    # extend default values for unspecified samples
    if len(args.rad) < len(args.inputs):
        args.rad.extend([defRad] * (len(args.inputs) - len(args.rad)))
    if len(args.thd) < len(args.inputs):
        args.thd.extend([defThd] * (len(args.inputs) - len(args.thd)))
else:
    # make a Cartesian product of sample value pairs
    I, R, T, B = [], [], [], []
    for element in itertools.product(args.rad, args.thd, args.binn):
        I.append(args.inputs[0])
        R.append(element[0])
        T.append(element[1])
        B.append(element[2])
    args.inputs, args.rad, args.thd, args.binn = I, R, T, B

if len(args.binn) < len(args.inputs):
    args.binn.extend([defBin] * (len(args.inputs) - len(args.binn)))
