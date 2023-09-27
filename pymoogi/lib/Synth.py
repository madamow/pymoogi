##############################################
# Synth module
##############################################
import matplotlib
import matplotlib.pyplot as plt
import copy
import time
import scipy.constants as sc
import scipy.optimize as so
import numpy as np
from matplotlib import rcParams
from matplotlib import ticker
import Common_functions as cf
from read_out_files import out2_synth
from solar_abund import get_solar_abund
from Smoothing import smooth_synspec, smooth_in_use


light_speed = sc.c * 0.001
solar = get_solar_abund()

smooth_strings = {
    'g':  'FWHM OF THE GAUSSIAN FUNCTION',
    'l':  'FWHM OF THE LORENTZIAN FUNCTION',
    'm':  'MACROTURBULENT VELOCITY',
    'v':  'STELLAR vsini',
    'ld': 'LIMB DARKENING COEFFICIENT'}


def print_options():
    print("OPTIONS?    s=new smoothing     r=rescale obs.")
    print("            a=add # to obs.     h=hardcopy")
    print("            c=change bounds     q=quit")
    print("            m=redo same plot    o=orig. plot bounds")
    print("            v=velocity shift    w=wavelength shift ")
    print("            z=use zoom button   p=cursor position")
    print("            t=change title      f=postscript file ")
    print("            n=new abundances    d=obs/syn deviation")
    print("            l=add veiling       u=undo all; replot")
    print("\nWhat is your choice? ")


class SynthPlot(object):

    def __init__(self, org_pars):
        self.org_pars = org_pars
        self.pars = copy.deepcopy(self.org_pars)
        self.smoothlist = []

        if list(self.pars['abundances'].keys())[0] == 99:
            dm = 'Changing'
        else:
            dm = 'ALL'

        self.out2 = out2_synth(self.pars['summary_out'], delimiter=dm)
        points = len(self.out2[0][-1])
        self.slam, step = np.linspace(self.pars['synlimits'][0],
                                      self.pars['synlimits'][1], points,
                                      retstep=True)

        # check if the step is the same
        if step == self.pars['synlimits'][2]:
            print("All good")

        # get synthetic spectra
        if not self.pars['smooth']:
            self.pars['smooth']['type'] = 'n'

        if self.pars['smooth']['type'] == 'n':
            self.sflux = [s[-1] for s in self.out2]
        else:
            self.sflux = smooth_synspec(self.out2, self.pars['smooth'])

        # Set initial plot params
        if not self.pars['plotpars']:
            self.pars['plotpars']['plotlim'] = self.pars['synlimits']
            self.pars['plotpars']['shift'] = [0., 0., 0., 1.]

        self.m, self.ls = ['', '-']
        if len(self.slam) < 500:
            self.m, self.ls = ['.', '']

        self.p2_flag = False
        self.flag = ''
        self.obs_in_flag = False
        self.obs = np.array([])

        if 'observed_in' in self.pars:
            self.obs_org = np.loadtxt(self.pars['observed_in'])
            self.obs_in_flag = True
            self.obs = np.copy(self.obs_org)

        self.points = []
        if self.pars['plotpars']:
            self.xylim = self.pars['plotpars']['plotlim']
        else:
            self.xylim = [float(self.pars['synlimits'][0][0]),
                          float(self.pars['synlimits'][0][1]), 0., 1.05]
        self.driver = 'synth'
        self.labels = [None] * self.pars['syn_no']

        self.fig, self.ax = plt.subplots()
        try:
            self.mh = float(self.out2[0][1].split("=")[-1])
        except TypeError:
            self.mh = 0.

    def ax_plot(self):
        # some basic formatting on plot

        if self.obs_in_flag:
            self.ax.plot(self.obs[:, 0], self.obs[:, 1],
                         ls=self.ls, marker=self.m,
                         color=rcParams['lines.color'])

        if self.pars['plotpars']:
            self.xylim = self.pars['plotpars']['plotlim']
            self.ax.set_xlim(self.xylim[0], self.xylim[1])
            self.ax.set_ylim(self.xylim[2], self.xylim[3])

        # Plot syntetic spectra
        colors = []

        for i, line in enumerate(self.sflux):
            ssp = self.ax.plot(self.slam, line, label=self.labels[i])
            colors.append(ssp[0].get_color())
        # Create legend
        try:
            legend = self.ax.legend(loc=3, frameon=False)
            for color, text in zip(colors, legend.get_texts()):
                text.set_color(color)
        except AttributeError:
            print("Error while creating a legend")
            pass

    def bx_plot(self):
        # Plot O-C on second panel
        # bx.xaxis.set_minor_locator( ticker.AutoMinorLocator() )
        yoc = np.interp(self.slam, self.obs[:, 0], self.obs[:, 1])

        colors = []
        for spec in self.sflux:
            oc = self.bx.plot(self.slam, yoc - spec,
                              label=round(np.std(yoc - spec, ddof=1), 4))
            colors.append(oc[0].get_color())
        self.bx.axhline(0., ls='dotted', color='r')

        # Set legend
        legend = self.bx.legend(loc=3, frameon=False)
        for color, text in zip(colors, legend.get_texts()):
            text.set_color(color)

    def isotope_labels(self):
        s = 'Isotopes:\n'
        for item in self.pars['isotopes']:
            iso_labels = "/".join(list(map(str, self.pars['isotopes'][item])))
            s = s + str(item) + ": " + iso_labels + "\n"
        return s

    def draw_marker(self, x, y):
        lbl = str(round(x, 2))+"\n"+str(round(y, 2))

        plt.annotate(lbl, xy=(x, y),  xycoords='data',
                     arrowprops=dict(arrowstyle='->', color='r'),
                     xytext=(x, y-0.15), fontsize=10, textcoords='data',
                     horizontalalignment='center', verticalalignment='top')

    def mark_points(self, event):
        # Put an arrow with x,y coords if user clicks on plot
        self.draw_marker(event.xdata, event.ydata)
        self.points.append([event.xdata, event.ydata])

    def on_xlims_change(self, axes):
        self.xylim[0], self.xylim[1] = axes.get_xlim()

    def on_ylims_change(self, axes):
        self.xylim[2], self.xylim[3] = axes.get_ylim()

    def do_plot(self):
        if list(self.pars['abundances'].keys())[0] == 99:
            dm = 'Changing'
        else:
            dm = 'ALL'
        self.out2 = out2_synth(self.pars['summary_out'], delimiter=dm)
        points = len(self.out2[0][-1])
        self.slam, step = np.linspace(self.pars['synlimits'][0],
                                      self.pars['synlimits'][1],
                                      points, retstep=True)

        if self.pars['smooth']['type'] == 'n':
            self.sflux = [s[-1] for s in self.out2]
        else:
            self.sflux = smooth_synspec(self.out2, self.pars['smooth'])

        # Create labels
        for i, spec in enumerate(self.sflux):
            s = ''
            if dm == 'ALL':
                for elem in self.out2[i][2]:
                    s += elem[0] + "=" + elem[1] + " "
            else:
                for elem in self.out2[i][2]:
                    s += '[M/H] FOR ALL ELEMENTS: ' + elem[1] + " "

            self.labels[i] = s.strip()

            if self.pars['veil'] > 0.0:
                veil = float(self.pars['veil'])
                self.sflux[i, 1, :] = (spec[1] + veil)/(1. + veil)

        if self.p2_flag is True and self.obs_in_flag is True:
            self.ax = plt.subplot2grid((2, 1), (0, 0))
            self.bx = plt.subplot2grid((2, 1), (1, 0), sharex=self.ax)
            self.ax_plot()

            self.bx_plot()
            plt.setp(self.ax.get_xticklabels(), visible=False)
            plt.subplots_adjust(hspace=0.)

            self.bx.set_xlabel('Wavelength')
            self.bx.set_ylabel('Obs - comp')
        else:
            self.ax = plt.subplot2grid((1, 1), (0, 0))
            self.ax_plot()
            self.ax.set_xlabel('Wavelength')

        self.ax.set_ylabel('Rel. flux')
        self.ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        self.ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
        self.ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())
        x_formatter = ticker.ScalarFormatter(useOffset=False)
        self.ax.xaxis.set_major_formatter(x_formatter)

        # Print input files' names
        if self.obs_in_flag:
            files_info = self.pars['observed_in'] + "\n"
            files_info += self.pars['lines_in'] + "\n"
            files_info += self.pars['model_in'] + "\n"
        else:
            files_info = self.pars['lines_in'] + "\n"
            files_info += self.pars['model_in'] + "\n"

        # Set smoothing info:
        if self.pars['smooth']:
            smo_info = "smoothing:"
            slist = smooth_in_use(self.pars['smooth'])
            for stype in slist:
                smo_info += f" {stype}={self.pars['smooth'][stype]}"

        extra_info = files_info + smo_info + "\n"

        # Set isotopes labels
        if 'isotopes' in list(self.pars.keys()):
            iso_txt = self.isotope_labels() + "\n"
            extra_info = extra_info + iso_txt

        self.ax.text(0.99, 0.01, extra_info,
                     horizontalalignment='right',
                     verticalalignment='bottom',
                     transform=self.ax.transAxes)

        # Draw markers
        if len(self.points) != 0:
            for x, y in self.points:
                self.draw_marker(x, y)

        plt.sca(self.ax)
        self.ax.callbacks.connect('xlim_changed', self.on_xlims_change)
        self.ax.callbacks.connect('ylim_changed', self.on_ylims_change)

    def set_cursor(self):
        cid = plt.gcf().canvas.mpl_connect('button_press_event',
                                           self.mark_points)
        print("Click on the plot window to mark a point(s)")
        print("and press enter when you get all markers you wanted...")
        print("or type c to remove all previous points")
        a = input()
        plt.gcf().canvas.mpl_disconnect(cid)
        if a == 'c':
            self.points = []

    def change_plotlim(self):

        sides = ['LEFT WAVELENGTH', 'RIGHT WAVELENGTH',
                 'BOTTOM RELATIVE FLUX', 'TOP RELATIVE FLUX']

        for i, lbl in enumerate(sides):
            print(f"{sides[i]} ({self.pars['plotpars']['plotlim'][i]}): ")
            self.pars['plotpars']['plotlim'][i] = cf.check_if_number()

    ####################################################################
    # Change smoothing
    ####################################################################
    def ask_for_smooth(self, slab):
        print(f"GIVE THE {smooth_strings[slab]}:")
        val = cf.check_if_number()
        return float(val)

    def change_smoothing(self):
        # Last settings for smoothing
        try:
            print(f"Previous setting: {self.pars['smooth']['type']} \n")
        except IndexError:
            pass

        print("  SMOOTHING: n=NONE, g=GAUSS, l=LORENZ, \
        v=ROTATION, m=MACROTURBULENCE\n \
                    c=v+g, d=m+g, r=m+v+g, p=VARIABLE GAUSS")
        smo = input()
        self.pars['smooth']['type'] = smo

        if smo == 'n':
            self.pars['smooth']['n'] = None
        elif smo in ['g', 'l', 'm']:
            self.pars['smooth'][smo] = self.ask_for_smooth(smo)
        elif smo == 'v':
            self.pars['smooth']['v'] = self.ask_for_smooth(smo)
            self.pars['smooth']['limbdark'] = self.ask_for_smooth('ld')
        elif smo == 'c':
            self.pars['smooth']['type']['v'] = self.ask_for_smooth('v')
            self.pars['smooth']['limbdark'] = self.ask_for_smooth('ld')
            self.pars['smooth']['type']['g'] = self.ask_for_smooth('g')
        elif smo == 'd':
            self.pars['smooth']['type']['m'] = self.ask_for_smooth('m')
            self.pars['smooth']['type']['g'] = self.ask_for_smooth('g')
        elif smo == 'r':
            self.pars['smooth']['type']['m'] = self.ask_for_smooth('m')
            self.pars['smooth']['type']['v'] = self.ask_for_smooth('v')
            self.pars['smooth']['limbdark'] = self.ask_for_smooth('ld')
            self.pars['smooth']['type']['g'] = self.ask_for_smooth('g')

    ####################################################################
    # Apply shifts to observed spectrum
    ####################################################################

    def apply_shifts(self):
        # watch for double shifts!
        v_shift, w_shift, a_fac, m_fac = self.pars['plotpars']['shift']

        self.obs[:, 0] = self.obs_org[:, 0] + float(w_shift)
        l_shift = v_shift / light_speed
        dop_fact = np.sqrt((1.0 + l_shift) / (1.0 - l_shift))
        self.obs[:, 0] = self.obs_org[:, 0] * dop_fact
        self.obs[:, 1] = self.obs_org[:, 1] * float(m_fac) + float(a_fac)

    def find_multip_res(self, factor, d):
        yobs, model = d
        if self.flag == 'r':
            newf = yobs * factor
        elif self.flag == 'a':
            newf = yobs - factor
        return newf - model

    def find_multip(self):
        syntf = np.average(self.sflux, axis=0)
        obsf = np.interp(self.slam, self.obs_org[:, 0], self.obs_org[:, 1])
        factor = so.leastsq(self.find_multip_res, [1.],
                            args=([obsf, syntf]), full_output=1)
        return round(factor[0][0], 2)

    def rescale_flux(self):
        if self.flag == 'r':
            print("MULTIPLY THE OBSERVED POINTS BY WHAT FACTOR?")
        else:
            print("ADD WHAT NUMBER TO THE OBSERVED POINTS?")

        print("press 'a' to find this factor automatically\n")
        rfactor = input()

        if rfactor == 'a':
            rfactor = str(self.find_multip())
            print(f'Your new factor is: {rfactor}')
            time.sleep(2.0)
        else:
            rfactor = cf.check_if_number(checkval=rfactor)
            time.sleep(2.0)

        if self.flag == 'r':
            self.pars['plotpars']['shift'][3] = rfactor
        elif self.flag == 'a':
            self.pars['plotpars']['shift'][2] = rfactor

        # Check if user uses additive and multiplicative shift at the same time
        message = "You cannot use additive shift "
        message += "and multiplicative shift at the same time.\n"

        if self.pars['plotpars']['shift'][2] != 0.0 and self.flag == 'r':
            message += " Setting additive shift to 0\nPress enter to continue"
            self.pars['plotpars']['shift'][2] = '0.0'
            print(message)
            input()

        elif self.pars['plotpars']['shift'][3] != 1.0 and self.flag == 'a':
            message += "Setting multipl. shift to 1\nPress enter to continue"
            self.pars['plotpars']['shift'][3] = '1.0'
            print(message)
            input()

    def v_shift(self):
        print("SHIFT THE OBSERVED POINTS BY WHAT VELOCITY (KM/S)?")
        rfactor = cf.check_if_number()
        self.pars['plotpars']['shift'][0] = rfactor
        # Check if w_fac is 0, if not - change it to 0
        if float(self.pars['plotpars']['shift'][1]) != 0.0:
            print("You cannot use wavelength shift and velocity\n \
            shift at the same time. Setting wavelength shift to 0")
            self.pars['plotpars']['shift'][1] = '0.0'
            print("Press any key to continue")
            input()

    def w_shift(self):
        print("SHIFT THE OBSERVED POINTS BY WHAT WAVELENGTH?")
        rfactor = cf.check_if_number()
        self.pars['plotpars']['shift'][1] = rfactor
        # Check if v_fac is 0, if not - change it to 0
        if float(self.pars['plotpars']['shift'][0]) != 0.0:
            print("You cannot use wavelength shift and velocity\n \
            shift at the same time. Setting velocity shift to 0")
            self.pars['plotpars']['shift'][0] = '0.0'
            print("Press enter to continue")
            input()

    ####################################################################
    # Add veil
    ####################################################################
    def add_veil(self):
        print("This option was created for pre Main-Sequence stars")
        print("Use it wisely! Setting veiling to 0.0 will remove \
        veiling from synthetic spectra. \n")

        print(f"WHAT IS THE ADDITIONAL FLUX IN TERMS OF CONTINUUM? "
              f"[{self.pars['veil']}]")

        veil = cf.check_if_number()
        self.pars['veil'] = veil

    ####################################################################
    # Change abundances and isotopes
    ####################################################################
    def change_abund(self):
        if 'abundances' not in self.pars:
            self.pars['abundances'] = {}

        print("Which element to change?")
        a_id = cf.check_if_number(expect_type='int')
        print("n = new abundances, or z = zero offsets?")
        flag = input()
        print("Enter the new abundances or offsets on the line below :")
        new = input().split(None)

        if a_id in self.pars['abundances'] and a_id != 99:
            if flag == 'n':
                new_off = []
                for a in new:
                    new_off.append("%.2f" % (float(a) - solar[a_id] - self.mh))
                    self.pars['abundances'][a_id] = new_off
            elif flag == 'z':
                self.pars['abundances'][a_id] = new
        elif int(a_id) == 99:
            for index, val in enumerate(self.pars['abundances']):
                self.pars['abundances'][a_id] = new
        else:
            self.pars['abundances'][a_id] = new

    def change_isotopes(self):
        print("\nOptions: c = change an isotopic factor")
        print("         n = enter a new isotope ")
        print("What is your choice?")
        flag = input()

        if flag == 'c':
            print("Which isotope number from the list?")
            i_id = cf.check_if_number(expect_type='int')
            print("What are the new division factors?")
            new = input().split(None)
            iso_list = list(self.pars['isotopes'].keys())
            self.pars['isotopes'][iso_list[i_id-1]] = new

        elif flag == 'n':  # add new entry to isotopes table
            print("What is the new isotope designation?")
            new_iso = cf.check_if_number()

            print("What are its division factors?")
            new_fac = input().split(None)

            if 'isotopes' not in self.pars:
                self.pars['isotopes'] = {}

            self.pars['isotopes'][new_iso] = new_fac

    def change_syn_no(self):
        print("How many synths?")
        syn_no = cf.check_if_number(expect_type='int')

        for tname in ['isotopes', 'abundances']:
            if tname in self.pars:
                for key in self.pars[tname]:
                    self.pars[tname][key] = self.pars[tname][key][:syn_no]

    def abundances(self):
        iterate = True
        # cf.clear()
        while iterate:
            # cf.clear()
            cf.print_driver(self.driver)

            print("element, abundance offsets OR isotope number, "
                  "isotope name, factors")

            if 'abundances' in self.pars:
                for elem in self.pars['abundances'].keys():
                    id_elem = "".join(f"{float(i):>4.2f} "
                                      for i in self.pars['abundances'][elem])
                    print(f"{''} {elem:>10s} {id_elem}")
                print("")

            if 'isotopes' in self.pars:
                for i, elem in enumerate(list(self.pars['isotopes'].keys())):
                    id_iso = "".join(f"{float(i):>10.2f} "
                                     for i in self.pars['isotopes'][elem])
                    print(f"{int(i + 1):3d} {elem:>10.4f} {id_iso}")

            print(f"\n{'Options:':>10s} {'c = change abundance':<25s} "
                  f"{'i = change isotopic ratio':<25s}")
            print(f"{'':>10s} {'n = change # syntheses':<25s} "
                  f"{'q = rerun syntheses':<25s} {'x = exit':<10s}")

            print("\n What is your choice?")

            aopt = input()

            if aopt == 'c':
                self.change_abund()
            elif aopt == 'n':
                self.change_syn_no()
            elif aopt == 'i':
                self.change_isotopes()
            elif aopt == 'q':  # rerun synthesis
                cf.run_moog(self.pars)
                iterate = False
            elif aopt == 'x':  # Forget all changes
                if 'abundances' in list(self.pars.keys()):
                    self.pars['abundances'] = self.org_pars['abundances']
                if 'isotopes' in list(self.pars.keys()):
                    self.pars['isotopes'] = self.org_pars['isotopes']
                iterate = False

    ####################################################################
    # Create hardcopy of plot
    ####################################################################
    def hardcopy(self):
        for ax in self.fig.axes:
            ax.xaxis.label.set_color('k')
            ax.yaxis.label.set_color('k')
            ax.tick_params(axis='y', which='both', colors='k')
            ax.tick_params(axis='x', which='both', colors='k')
            ax.patch.set_facecolor('w')
            for child in ax.get_children():
                if isinstance(child, matplotlib.spines.Spine) or \
                        isinstance(child, matplotlib.text.Annotation) or \
                        isinstance(child, matplotlib.text.Text):
                    child.set_color('k')

            ax.title.set_color('k')
            legend = ax.get_legend()
            for text in legend.get_texts():
                text.set_color('k')

        for artist in plt.gca().get_children():
            if hasattr(artist, 'get_label') and artist.get_label() == '_line0':
                artist.set_color('k')

        if self.flag == 'f':
            print("Give the file name for the POSTSRIPT plot image:")
            tf = input() + ".pdf"
        else:
            tf = "plot_"+cf.id_generator() + ".pdf"

        plt.savefig(tf, facecolor='white', bbox_inches='tight',
                    orientation='landscape')

    ####################################################################
    def run_synth(self):
        if self.obs_in_flag is True and self.pars['plotpars']:
            self.apply_shifts()

        quit_moog = False
        while not quit_moog:
            self.do_plot()
            # cf.clear()

            cf.print_driver(self.driver)
            if not self.obs_in_flag:
                print(" !!! No observed spectrum provided")
                print(" !!! Operations on observed spectrum are not active\n")

            print_options()

            self.flag = input()
            if self.flag == 'q':
                quit_moog = True
            elif self.obs_in_flag and (self.flag == 'a' or self.flag == 'r'):
                self.rescale_flux()
                self.apply_shifts()
            elif self.obs_in_flag and self.flag == 'w':
                self.w_shift()
                self.apply_shifts()
            elif self.obs_in_flag and self.flag == 'v':
                self.v_shift()
                self.apply_shifts()
            elif self.flag == 'h' or self.flag == 'f':
                self.hardcopy()
            elif self.flag == 'c':
                self.change_plotlim()
            elif self.flag == "m":
                self.do_plot()
            elif self.flag == 's':
                self.change_smoothing()
            elif self.flag == 'n':
                self.abundances()
            elif self.flag == 'u':
                self.pars = copy.deepcopy(self.org_pars)
                self.apply_shifts()
                cf.run_moog(self.pars)
            elif self.flag == 'l':
                self.add_veil()
            elif self.flag == 'p':
                self.set_cursor()
            elif self.flag == 'z':
                print("Use zoom button in plot window")
            elif self.flag == 'd':
                self.p2_flag = True
            elif self.flag == 't':
                print("Enter new title")
                self.pars['title'] = input()
            elif self.flag == 'o':
                self.pars['plotpars'][1] = self.org_pars['plotpars'][1]
                self.xylim = list(map(float, self.pars['plotpars'][1]))
                self.p2_flag = False
            else:
                print("Do not understand")
                time.sleep(0.5)

            plt.clf()
