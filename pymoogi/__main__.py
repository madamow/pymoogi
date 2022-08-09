#!/usr/bin/env python

import os
import sys

path = os.path.dirname(os.path.realpath(__file__))  # directory of pymoogi
print(path)
# location of pyEW functions:
sys.path.append("%s/lib/" % path)

from Common_functions import *
import matplotlib.pyplot as plt
from plot_style import SM_style
from Synth import SynthPlot
from Abfind import AbfindPlot

required = ['numpy', 'scipy', 'matplotlib']
for package in required:
    try:
        exec('import {}'.format(package))
    except ImportError:
        print(('\nYou need to install the package "{}"'.format(package)))
        exit()

plt.switch_backend('qt5Agg')

def main():

    clear()
    syn_file = sys.argv[1]
    driver, params = list_to_dict(open(syn_file).read())

    # Run MOOG for user's par file
    try:
        run_moog(driver, params)
    except:
        print("#####################\n Cannot run MOOG.")
        print("Check batch.par file and your input file for errors.")
        exit()

    params['veil'] = 0.
    params['title'] = ""

    SM_style()
    plt.ion()

    if driver == 'synth' and int(params['plot'][0]) > 0:
        # show plot
        # parameters for plot are defined by user
        p = SynthPlot(params)
        p.run_synth()
    elif driver == 'synth' and params['plotpars'][0] == 1 and int(params['plot'][0]) == 0:
        # do not show plot
        # creates two output files, no output with smoothed synthetic spectra
        run_moog(driver, params)

    elif driver == 'abfind':
        p = AbfindPlot(params)
        p.run()

    elif driver == 'ewfind':
        print_driver('ewfind')
        run_moog(driver, params)
        print("All done! Check outputfiles for %s driver" % driver)

    elif driver == 'blends':
        print_driver('blends')
        run_moog(driver, params)
        print("All done! Check outputfiles for %s driver" % driver)

if __name__ == "__main__":

    main()