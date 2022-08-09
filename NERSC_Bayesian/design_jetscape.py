"""
Generates Latin-hypercube parameter designs

This script is borrowed from Yingru. It will generate a text file, a hdf5 that contains all the design points, and also different folders 
that contain the JETSCAPE xml file that is using the parameters at the sampled design points. 

"""

import itertools
import logging
import subprocess
import h5py
import numpy as np
import argparse
import fileinput
import pathlib

import os
import os.path
import sys



def checkAndBuildDir(checkDir):
    if (not os.path.isdir(checkDir)):
        print("Creating directory \""+checkDir+"\" ...")
        os.mkdir(checkDir)

def generate_design(npoints, ndim, low=None, high=None, seed = np.random.randint(2**30)):
    """
    generate a maximin Latin-hypercube sample with the given number of points, dimensions and random seed
    """

    logging.debug(
        'generating maximin LHS: '
        'npoints = %d, ndim = %d, seed = %d', 
        npoints, ndim, seed
    )

    proc = subprocess.run(
        ['R', '--slave'],
        input="""
        library('lhs')
        set.seed({})
        write.table(maximinLHS({}, {}), col.names=FALSE, row.names=FALSE)
        """.format(seed, npoints, ndim).encode(),
        stdout = subprocess.PIPE,
        check=True
    )

    lhs = np.array([l.split() for l in proc.stdout.splitlines()], dtype=float)

    if low is None and high is None:
        return lhs

    # rescale the hypercube to requested range
    low = np.zeros(ndim) if low is None else np.asarray(low)
    high = np.ones(ndim) if high is None else np.asarray(high)

    return lhs * (high - low) + low

def hadronizeWith(outputFolder, fileName, id, data):
    OutDir = outputFolder+"/"+str(id)+"/"

    checkAndBuildDir(OutDir)

    inputfileName = OutDir+"/jetscape_init.xml"
    os.system("cp "+" ./"+fileName+" " + inputfileName)

    for line in fileinput.input([inputfileName], inplace=True):
        if '<alphas>' in line:
            line = '<alphas> '+str(data[0])+' </alphas>\n'

        if '<qhatA>' in line:
            line = '<qhatA> '+str(data[1])+' </qhatA>\n'
        
        if '<qhatB>' in line:
            line = '<qhatB> '+str(data[2])+' </qhatB>\n'

        if '<Q0>' in line:
            line = '<Q0> '+str(data[3])+' </Q0>\n'

        sys.stdout.write(line)




def main():
    parser = argparse.ArgumentParser(
        description = 'create the Latin-hypercube design'
    )

    parser.add_argument('--output-file', help='HDF5 outputfile')
    parser.add_argument('--inputfile-dir', help='directory to place the OSG input files')
    args = parser.parse_args()

    if args.output_file is None and args.inputfile_dir is None:
        parser.print_help()
        return


    ## define the design parameters
    ##     label         key         low         high        guess
    design_params = [
        (r'alpha',    'alpha',      0.1,        0.5,        0.3),
        (r'c_1',  'c_1',    1,        15.0,        10.0),
        (r'c_2','c_2',  50,        300.0,        100),
        (r'Q_s','Q_s',  1.5,        4,        2),
    ]

    zip_params = zip(*design_params)
    labels = list(next(zip_params))
    keys = list(next(zip_params))
    low, high, guess = map(np.array, zip_params)
    ndim = len(design_params)

    ## create a dict of main and validation designs
    design = {
        name: generate_design(npoints, ndim, low=low, high=high, seed = seed)
        for (name, npoints, seed) in [
            ('main',        50,    716535127),
            ('validation',  10,     219473425),
        ]
    }

    ## sort themain design by normalized distance from the guess point
    ## this way better points will in general run earlier
    #design['main'] = design['main'][np.square((desugb['main'] - guess)/(high - low)).sum(axis=1).argsort()]

    ## write HDF5 file
    if args.output_file:
        with h5py.File(args.output_file, 'w') as f:
            g = f.create_group('design')
            for name, data in design.items():
                g.create_dataset(name, data=data)

            f.create_dataset('range', data = np.column_stack([low, high]))
            d = f.create_dataset('labels', shape=(len(labels),), dtype=h5py.special_dtype(vlen=str))
            d[:] = labels
    
    ## write OSG input files
    if args.inputfile_dir:
        file_template = ''.join(
            '{} = {}\n'.format(key, ' '.join(args)) for (key, *args) in 
            [[
                'alpha',
                '{alpha}',
            ],[
                'c_1',
                '{c_1}',
            ],[
                'c_2',
                '{c_2}',
            ],[
                'Q_s',
                '{Q_s}',
            ]]
        )

        print(design)
        
        for name, array in design.items():
            destdir = os.path.join(args.inputfile_dir, name)
            os.makedirs(destdir, exist_ok=True)

            ndigits = int(np.log10(array.shape[0]) + 1)
            path_template = os.path.join(destdir, '{:0' + str(ndigits) + 'd}')

            for n, row in enumerate(array):
                hadronizeWith(destdir, "jetscape_init.xml", n, row)
                #with open(path_template.format(n), 'w') as f:
                #    params = dict(zip(keys, row))
                #    f.write(file_template.format(**params))
    

if __name__ == '__main__':
    main()
