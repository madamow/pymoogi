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


def istype(value, expect_type='float'):
    # Check if value is a float
    if expect_type == 'float':
        try:
            float(value)
            return True
        except ValueError:
            return False
    elif expect_type == 'int':
        try:
            int(value)
            return True
        except ValueError:
            return False
    else:
        return False


def check_if_number(checkval=None, expect_type='float'):
    if not checkval:
        checkval = input()
    while not istype(checkval, expect_type=expect_type):
        print(f"Your value is not a(n) {expect_type} type number. Try again")
        checkval = input()

    if expect_type == 'float':
        return float(checkval)
    elif expect_type == 'int':
        return int(checkval)
    else:
        return None


def check_syn_no(dict_par):
    synths = []
    if dict_par['abundances']:
        for elem in dict_par['abundances']:
            synths.append(len(dict_par['abundances'][elem]))
    if dict_par['isotopes']:
        for elem in dict_par['isotopes']:
            synths.append(len(dict_par['isotopes'][elem]))

    if len(list(set(synths))) != 1:
        print('Different number of sythesis for elements')
        synNo = min(list(set(synths)))
    else:
        synNo = list(set(synths))[0]

    return synNo


# Recreate back proper string
def dict_to_str(dict_par):
    s = dict_par['driver'] + "\n"
    keys = ['standard_out', 'summary_out', 'model_in',
            'lines_in', 'strong', 'stronglines_in', 'freeform', 'opacit',
            'observed_in', 'atmosphere',
            'trudamp', 'units', 'lines', 'molecules',
            'flux/int', 'fluxlimits', 'coglimits',
            'iraf', 'damping', 'histogram']

    for elem in keys:
        if elem in list(dict_par.keys()):
            s = s + elem + " "+str(dict_par[elem]) + "\n"

    if 'abundances' in dict_par:
        no_el = str(len(dict_par['abundances']))
        s = s + "abundances " + no_el + " " + str(dict_par['syn_no']) + "\n"
        for elem in dict_par['abundances']:
            ab_string = ' '.join(list(map(str, dict_par['abundances'][elem])))
            s = s + "    " + str(elem) + "    " + ab_string + "\n"

    if 'isotopes' in dict_par:
        no_el = str(len(dict_par['isotopes']))
        s = s + "isotopes " + no_el + " " + str(dict_par['syn_no']) + "\n"
        for elem in dict_par['isotopes']:
            iso_string = ' '.join(list(map(str, dict_par['isotopes'][elem])))
            s = s + "    " + str(elem) + "    " + iso_string + "\n"

    if 'synlimits' in dict_par:
        s = s + "synlimits\n"
        s = s + "    "+' '.join(list(map(str, dict_par['synlimits']))) + "\n"

    if 'blenlimits' in dict_par:
        s = s + "blenlimits\n"
        s = s + "    "+' '.join(dict_par['blenlimits']) + "\n"

    if 'obspectrum' in dict_par:
        s = s + "obspectrum " + dict_par['obspectrum'][0] + "\n"

    return s


def run_moog(pars):
    print("Calling MOOG")
    if pars['driver'] == 'synth':
        pars['syn_no'] = check_syn_no(pars)
    st = dict_to_str(pars)
    print(pars)
    with open('./batch.par', 'w') as batchpar:
        batchpar.write(st)
    sp.check_output('echo "batch.par\nq" | %s/MOOG' % MOOG_HOME, shell=True)


def print_driver(driver):
    print("**************************************************************")
    print("MOOG IS CONTROLLED BY DRIVER", driver)
    print("**************************************************************\n")


def id_generator(size=3, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def do_stats(x, y):
    a, b = np.polyfit(x, y, 1)
    c = ss.pearsonr(x, y)[0]
    return a, b, c


def print_stats(t):
    print("Here are abundances for", ELEMENTS[int(t[0, 1])])
    print(f"{'wavelength':>10s} {'ID':>5s} {'EP':>8s} {'logGF':>8s} "
          f"{'EWin':>8s} {'logRWin':>7s} {'abund':>7s} {'delavg':>8s}")

    for item in t[t[:, 0].argsort()]:
        print(f"{item[0]:>10.2f} {item[1]:>5.1f} {item[2]:>8.2f}"
              f"{item[3]:>8.2f} {item[4]:>7.2f} {item[5]:>7.3f} "
              f"{item[6]:>8.3f} {item[7]:>8.3f}")
    if t.shape[0] == 1.:
        print("Just one line, no stats")
    else:
        print(f"average abundance  = {np.average(t[:, 6]):>-9.3f} "
              f"std. deviation =  {np.std(t[:, 6], ddof=1):>-9.3f} "
              f"#lines = {len(t[:, 6]):3d}")
    if t.shape[0] > 3.:
        ep_stats = do_stats(t[:, 2], t[:, 6])
        print(f"E.P. correlation:  slope = {ep_stats[0]:>7.3f}  "
              f"intercept = {ep_stats[1]:>7.3f}  "
              f"corr. coeff. = {ep_stats[2]:>7.3f}")
        rw_stats = do_stats(t[:, 5], t[:, 6])
        print(f"R.W. correlation:  slope = {rw_stats[0]:>7.3f}  "
              f"intercept = {rw_stats[1]:>7.3f}  "
              f"corr. coeff. = {rw_stats[2]:>7.3f}")
        wav_stats = do_stats(t[:, 0], t[:, 6])
        print(f"wav. correl.:  slope = {wav_stats[0]:>7.3f}  "
              f"intercept = {wav_stats[1]:>7.3f}  "
              f"corr. coeff. = {wav_stats[2]:>7.3f}")
    else:
        print("No statistics done for E.P. trends")
        print("No statistics done for R.W. trends")
        print("No statistics done for wav. trends\n")
