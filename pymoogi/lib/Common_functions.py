import string
import os
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


# Recreate back proper string
def dict_to_str(dict_par):
    s = dict_par['driver'] + "\n"
    keys = ['standard_out', 'summary_out', 'smoothed_out', 'model_in',
            'lines_in', 'strong', 'stronglines_in', 'freeform', 'opacit',
            'observed_in', 'atmosphere',
            'trudamp', 'units', 'lines', 'molecules',
            'flux/int', 'fluxlimits', 'coglimits',
            'iraf', 'damping', 'histogram']

    for elem in keys:
        if elem in list(dict_par.keys()):
            s = s + elem + " "+str(dict_par[elem]) + "\n"

    if 'abundances' in list(dict_par.keys()):
        no_el = str(len(dict_par['abundances']))
        # Check if each element has the same number of abundances
        the_len = []
        for elem in dict_par['abundances']:
            the_len.append(len(dict_par['abundances'][elem]))
        if len(list(set(the_len))) != 1:
            raise ValueError('Different number of sythesis for elements')
            exit()
        else:
            no_ab = list(set(the_len))[0]
        s = s + "abundances " + no_el + " " + str(no_ab) + "\n"
        for elem in dict_par['abundances']:
            s = s + "    " + str(elem) + "    "
            s = s + (' '.join(list(map(str, dict_par['abundances'][elem])))) + "\n"

    if 'isotopes' in list(dict_par.keys()):
        no_el = str(len(dict_par['isotopes']))
        # Check if each element has the same number of abundances
        the_len = []
        for elem in dict_par['isotopes']:
            the_len.append(len(dict_par['isotopes'][elem]))
        if len(list(set(the_len))) != 1:
            raise ValueError('Different number of sythesis for elements')
            exit()
        else:
            no_ab = list(set(the_len))[0]
        s = s + "isotopes " + no_el + " " + str(no_ab) + "\n"
        for elem in dict_par['isotopes']:
            s = s + "    " + str(elem) + "    "
            s = s + (' '.join(list(map(str, dict_par['isotopes'][elem])))) + "\n"


    if 'synlimits' in list(dict_par.keys()):
        s = s + "synlimits\n"
        s = s + "    "+' '.join(dict_par['synlimits']) + "\n"

    if 'blenlimits' in list(dict_par.keys()):
        s = s + "blenlimits\n"
        s = s + "    "+' '.join(dict_par['blenlimits']) + "\n"


    if 'obspectrum' in list(dict_par.keys()):
        s = s + "obspectrum " + dict_par['obspectrum'][0] + "\n"

    return s


def run_moog(pars):
    print("Calling MOOG")
    st = dict_to_str(pars)

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
