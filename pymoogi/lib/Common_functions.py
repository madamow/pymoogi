import string
import os
import re
import numpy as np
import subprocess as sp
import scipy.stats as ss
import random
from elements import ELEMENTS

# Check if you have enviromental variable "MOOGPATH"
try:
    MOOG_HOME = os.environ['MOOGPATH']
    print("MOOGPATH =", MOOG_HOME)
except KeyError:
    print("MOOGPATH not found")
    print("Export MOOG path")
    exit()

# Check if you have executable MOOG file exists
if os.path.isfile(os.path.join(MOOG_HOME, "MOOG")):
    print("MOOG is ready")
else:
    print("Compile MOOG")
    exit()


def clear():
    os.system('clear')


def get_key(item):
    return item[0]


def isfloat(value):
    # Check if value can be float
    try:
        float(value)
        return True
    except ValueError:
        return False


def str_to_list(s):
    # Write long str as a list
    # divide long string, get lines without spaces
    
    # Trace and replace \r
    s = s.replace('\r', '').replace('\t', ' ')
    
    lines = s.split('\n')
    
    tab = []
    driver = lines[0]
    for line in lines[1:]:
        # Remove unneccesary spaces
        l_list = [_f for _f in line.split(" ") if _f]
        tab.append(l_list)

    return driver, [_f for _f in tab if _f]


def list_to_dict(sf):
    driver, tab = str_to_list(sf)
    smoothing_types = ['g', 'l', 'v', 'm', 'c', 'd', 'r']
    l_par = {'isotopes', 'abundances', 'plotpars', 'synlimits', 'blenlimits'}

    # Transform list to dict
    dict_par = {}
    for line in tab:
        if not isfloat(line[0]) and smoothing_types.count(line[0]) == 0:
            if not line[0] in l_par:
                dict_par[line[0]] = []
                dict_par[line[0]].append(line[1])
            else:
                dict_par[line[0]] = []
                ind = tab.index(line)

                if line[0] == 'abundances' or line[0] == 'isotopes':
                    dict_par[line[0]].append([line[1], line[2]])
                    iline = np.arange(ind + 1, 1 + ind + int(line[1]))
                    for i in iline:
                        dict_par[line[0]].append([tab[i][0], tab[i][1:]])
                elif line[0] == 'synlimits' or line[0] == 'blenlimits':
                    dict_par[line[0]].append(tab[ind + 1])
                elif line[0] == 'plotpars':
                    if line[1] == '1':
                        iline = np.arange(ind+1, ind+4)
                        dict_par[line[0]].append(1)
                        for i in iline:
                            dict_par[line[0]].append(tab[i])
                    else:  # default values are set for plotting parameters:
                        dict_par[line[0]].append(0)
    try:
        dict_par['abundances'][1:] = sorted(dict_par['abundances'][1:], key=get_key)
    except KeyError:
        pass

    try:
        dict_par['isotopes'][1:] = sorted(dict_par['isotopes'][1:], key=get_key)
    except KeyError:
        pass


    return driver, dict_par


# Recreate back proper string
def dict_to_str(driver, dict_par):
    s = driver + "\n"
    keys = ['standard_out', 'summary_out', 'smoothed_out', 'model_in',
            'lines_in', 'strong', 'stronglines_in', 'freeform', 'opacit',
            'observed_in', 'atmosphere',
            'trudamp', 'units', 'lines', 'molecules',
            'flux/int', 'fluxlimits', 'coglimits',
            'iraf', 'damping', 'plot', 'histogram']

    for elem in keys:
        if elem in list(dict_par.keys()):
            s = s + elem + " "+str(dict_par[elem][0]) + "\n"

    if 'abundances' in list(dict_par.keys()):
        no_ab = int(dict_par['abundances'][0][1])
        s = s + "abundances " + dict_par['abundances'][0][0] + " " + dict_par['abundances'][0][1] + "\n"
      
        for line in dict_par['abundances'][1:]:
            s = s + "    " + line[0] + "    "
            s = s + (' '.join(line[1][:no_ab])) + "\n"

    if 'isotopes' in list(dict_par.keys()):
        no_iso = int(dict_par['isotopes'][0][1])
        s = s + "isotopes " + dict_par['isotopes'][0][0] + " "+dict_par['isotopes'][0][1] + "\n"
        for line in dict_par['isotopes'][1:]:
            s = s + "    "+line[0] + "    "
            s = s + (' '.join(line[1][:no_iso])) + "\n"

    if 'synlimits' in list(dict_par.keys()):
        s = s + "synlimits\n"
        s = s + "    "+' '.join(dict_par['synlimits'][0]) + "\n"

    if 'blenlimits' in list(dict_par.keys()):
        s = s + "blenlimits\n"
        s = s + "    "+' '.join(dict_par['blenlimits'][0]) + "\n"

    if 'plotpars' in list(dict_par.keys()):
        s = s + "plotpars" + " " + str(dict_par['plotpars'][0]) + "\n"
        for line in dict_par['plotpars'][1:]:
            s = s+(' '.join(line)) + "\n"

    if 'obspectrum' in list(dict_par.keys()):
        s = s + "obspectrum " + dict_par['obspectrum'][0] + "\n"

    return s


def run_moog(driver, pars):
    print("Calling MOOG")
    st = dict_to_str(driver, pars)

    with open('./batch.par', 'w') as batchpar:
        batchpar.write(st)
    sp.check_output('echo "batch.par\nq" | %s/MOOG' % MOOG_HOME, shell=True)


def print_driver(driver):
    print("****************************************************************************")
    print("MOOG IS CONTROLLED BY DRIVER", driver)
    print("****************************************************************************\n")


def id_generator(size=3, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def do_stats(x, y):
    a, b = np.polyfit(x, y, 1)
    c = ss.pearsonr(x, y)[0]
    return a, b, c


def print_stats(t):
    print("Here are abundances for", ELEMENTS[int(t[0, 1])])
    print("%10s %5s %8s %8s %8s %7s %7s %8s" % \
          ("wavelength", "ID", "EP", "logGF", "EWin", "logRWin", "abund", "delavg"))
    for l in t[t[:, 0].argsort()]:
        print("%10.2f %5.1f %8.2f %8.2f %7.2f %7.3f %8.3f %8.3f" % \
                  (l[0], l[1], l[2], l[3], l[4], l[5], l[6], l[7]))
    if t.shape[0] == 1.:
        print("Just one line, no stats")
    else:
        print("average abundance  = %-9.3f std. deviation =  %-9.3f #lines = %3i" % \
              (np.average(t[:, 6]), np.std(t[:, 6], ddof=1), len(t[:, 6])))
    if t.shape[0] > 3.:
        print("E.P. correlation:  slope = %7.3f  intercept = %7.3f  corr. coeff. = %7.3f" % \
              (do_stats(t[:, 2], t[:, 6])))
        print("R.W. correlation:  slope = %7.3f  intercept = %7.3f  corr. coeff. = %7.3f" % \
              (do_stats(t[:, 5], t[:, 6])))
        print("wav. correl.:  slope = %7.3e  intercept = %7.3f  corr. coeff. = %7.3f\n" % \
              (do_stats(t[:, 0], t[:, 6])))
    else:
        print("No statistics done for E.P. trends")
        print("No statistics done for R.W. trends")
        print("No statistics done for wav. trends\n")
