#!/usr/bin/env python
"""Builds the documentaion. First it runs gendoc to create rst files for the source code. Then it runs sphinx make.
.. Warning:: This will delete the content of the output directory first! So you might loose data.
             You can use updatedoc.py -nod.
Usage, just call::

  updatedoc.py -h

"""
import argparse
import os
import shutil
import subprocess
import sys

import gendoc


def setup_argparse():
    """Sets up the argument parser and returns it

    :returns: the parser
    :rtype: :class:`argparse.ArgumentParser`
    :raises: None
    """
    thisdir = os.path.abspath(os.path.dirname(__file__))
    parser = argparse.ArgumentParser(
        description="Builds the documentaion. First it runs gendoc to create rst files\
        for the source code. Then it runs sphinx make.\
        WARNING: this will delete the contents of the output dirs. You can use -nod.")
    ipath = os.path.join(thisdir, '../{{ cookiecutter.repo_name  }}')
    ipath = os.path.normpath(ipath)
    idefault = [ipath]
    parser.add_argument('-i', '--input', nargs='+', default=idefault,
                        help='list of input directories. gendoc is called for every\
                        source dir.\
                        Default is \'%s\'.' % ', '.join(idefault))
    opath = os.path.join(thisdir, '{{ cookiecutter.apidoc }}')
    opath = os.path.normpath(opath)
    odefault = [opath]
    parser.add_argument('-o', '--output', nargs='+', default=odefault,
                        help='list of output directories. if you have multiple source\
                        directories, the corresponding output directorie is used.\
                        if there are less dirs than for source, the last output dir\
                        is used for the remaining source dirs.\
                        WARNING: the output directories are emptied by default. See -nod.\
                        Default is \'%s\'.' % ', '.join(odefault))
    gadefault = ['-T', '-f', '-e', '-o']
    parser.add_argument('-ga', '--gendocargs', nargs='*', default=gadefault,
                        help="list of arguments to pass to gendoc. use -gh for info.\
                        Default is \'%s\'" % ', '.join(gadefault))
    parser.add_argument('-nod', '--nodelete', action='store_true',
                        help='Do not empty the output directories first.')
    parser.add_argument('-gh', '--gendochelp', action='store_true',
                        help='print the help for gendoc and exit')
    mfdefault = 'sphinx-build'
    parser.add_argument('-mf', '--makefile', default=mfdefault,
                        help='the makefile to use. Default is %s' % mfdefault)
    madefault = ['-b', 'html', './', '_build/']
    parser.add_argument('-ma', '--makeargs', nargs='+', default=madefault,
                        help='arguments for the makefile.\
                        Default is \'%s\'.' % ', '.join(madefault))
    return parser


def prepare_dir(directory, delete=True):
    """Create apidoc dir, delete contents if delete is True.

    :param directory: the apidoc directory. you can use relative paths here
    :type directory: str
    :param delete: if True, deletes the contents of apidoc. This acts like an override switch.
    :type delete: bool
    :returns: None
    :rtype: None
    :raises: None
    """
    if os.path.exists(directory):
        if delete:
            print 'Deleting %s' % directory
            shutil.rmtree(directory)
            print 'Creating %s' % directory
            os.mkdir(directory)
    else:
        print 'Creating %s' % directory
        os.mkdir(directory)


def run_gendoc(source, dest, args):
    """Starts gendoc which reads source and creates rst files in dest with the given args.

    :param source: The python source directory for gendoc. Can be a relative path.
    :type source: str
    :param dest: The destination for the rst files. Can be a relative path.
    :type dest: str
    :param args: Arguments for gendoc. See gendoc for more information.
    :type args: list
    :returns: None
    :rtype: None
    :raises: SystemExit
    """
    args.insert(0, 'gendoc.py')
    args.append(dest)
    args.append(source)
    print 'Running gendoc.main with: %s' % args
    gendoc.main(args)


def run_make(makefile, args):
    """Run the sphinx make process

    :param makefile: the sphinx make file to run. e.g. make.bat
    :type makefile: str
    :param args: the arguments for the makefile
    :type args: list
    :returns: return code of the makeprocess
    :rtype: int
    :raises: None
    """
    args.insert(0, makefile)
    print 'Running sphinx make with: %s' % args
    rcode = subprocess.call(args, cwd=os.getcwd())
    return rcode


def main(argv=sys.argv):
    """Parse commandline arguments and run the tool

    :param argv: the commandline arguments
    :type argv: list
    :returns: None
    :rtype: None
    :raises: None
    """
    parser = setup_argparse()
    args = parser.parse_args()
    if args.gendochelp:
        sys.argv[0] = 'gendoc.py'
        genparser = gendoc.setup_parser()
        genparser.print_help()
        sys.exit(0)
    print 'Preparing output directories'
    print '='*80
    for odir in args.output:
        prepare_dir(odir, not args.nodelete)
    print '\nRunning gendoc'
    print '='*80
    for i, idir in enumerate(args.input):
        if i >= len(args.output):
            odir = args.output[-1]
        else:
            odir = args.output[i]
        run_gendoc(idir, odir, args.gendocargs)
    print '\nRunning sphinx'
    print '='*80
    run_make(args.makefile, args.makeargs)

if __name__ == '__main__':
    main()
