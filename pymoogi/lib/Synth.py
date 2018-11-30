##############################################
# Synth module
##############################################
import matplotlib
import matplotlib.pyplot as plt
import copy
import time
import numpy as np
import scipy.constants as sc
import scipy.optimize as so
from matplotlib import rcParams
from matplotlib import ticker
from Common_functions import *
from read_out_files import out2_synth, out3_synth

light_speed = sc.c * 0.001


class SynthPlot(object):

    def __init__(self, org_pars):
        self.org_pars = org_pars
        self.pars = copy.deepcopy(self.org_pars)
        self.p2_flag = False
        self.flag = ''
        self.obs_in_flag = False
        self.obs = np.array([])
        if 'observed_in' in self.pars.keys():
            self.obs = np.loadtxt(self.pars['observed_in'][0][1:-1])
            self.obs_in_flag = True

        self.points = []
        self.xylim = map(float, self.pars['plotpars'][1])
        self.driver = 'synth'     

    def print_options(self):
        print "OPTIONS?    s=new smoothing     r=rescale obs."
        print "            a=add # to obs.     h=hardcopy"
        print "            c=change bounds     q=quit"
        print "            m=redo same plot    o=orig. plot bounds"
        print "            v=velocity shift    w=wavelength shift "
        print "            z=use zoom button   p=cursor position"
        print "            t=change title      f=postscript file "
        print "            n=new abundances    d=obs/syn deviation"
        print "            l=add veiling       u=undo all; replot"
        print "\nWhat is your choice? "

    def ax_plot(self):
        # some basic formatting on plot
        if self.obs_in_flag:
            self.ax.plot(self.obs[:, 0], self.obs[:, 1], 'o', color=rcParams['lines.color'])
        self.ax.set_xlim(self.xylim[0], self.xylim[1])
        self.ax.set_ylim(self.xylim[2], self.xylim[3])

        # Plot syntetic spectra
        colors = []
        for i, line in enumerate(self.sflux):
            ssp = self.ax.plot(line[0], line[1], label=self.labels[i])
            colors.append(ssp[0].get_color())
        
        # Create legend
        try:
            legend = self.ax.legend(loc=3, frameon=False)
            for color, text in zip(colors, legend.get_texts()):
                text.set_color(color)
        except AttributeError:
            pass

    def bx_plot(self):
        # Plot O-C on second panel
        # bx.xaxis.set_minor_locator( ticker.AutoMinorLocator() )
        yoc = np.interp(self.sflux[0][0], self.obs[:, 0], self.obs[:,1])
    
        colors = []
        for spec in self.sflux:
            l = self.bx.plot(spec[0], yoc - spec[1],
                             label=round(np.std(yoc - spec[1], ddof=1), 4))
            colors.append(l[0].get_color())
        self.bx.axhline(0., ls='dotted', color='r')
    
        # Set legend
        legend = self.bx.legend(loc=3, frameon=False)
        for color, text in zip(colors, legend.get_texts()):
            text.set_color(color) 

    def isotope_labels(self):
        s = 'Isotopes:\n'
        for item in self.pars['isotopes'][1:]:
            s = s + item[0] + ": " + "/".join(item[1]) + "\n"
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
        self.out2 = out2_synth(self.pars['summary_out'][0][1:-1])
        self.out3 = out3_synth(self.pars['smoothed_out'][0][1:-1])
        self.sflux = np.array(copy.deepcopy(self.out3), dtype=float)
        
        # Create labels
        self.labels = []
        for i, spec in enumerate(self.sflux):
            s = ''
            for l in self.out2[i][2]:
                s = s + l[0] + "=" + l[1] + " "
            self.labels.append(s.strip())
            
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
        
        # Set title
        if self.pars['title'] == "":
            title_obj = self.ax.set_title(self.out2[0][1])
        else:
            title_obj = self.ax.set_title(self.pars['title'])

        # Print input files' names

        if self.obs_in_flag:
            files_info = self.pars['observed_in'][0] + "\n" + \
                         self.pars['lines_in'][0] + "\n" + self.pars['model_in'][0] + "\n"
        else:
            files_info = self.pars['lines_in'][0] + "\n" + self.pars['model_in'][0] + "\n"

        # Set smoothing info:
        smo_info = "smoothing: "+str(self.pars['plotpars'][3][0]) + " = "
        smo_nr = filter(lambda x: float(x) != 0, self.pars['plotpars'][3][1:])
        for item in smo_nr:
            smo_info = smo_info + item + ", "

        extra_info = files_info + smo_info + "\n"

        # Set isotopes labels
        if 'isotopes' in self.pars.keys():
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
        print "Click on the plot window to mark a point(s)"
        print "and press enter when you get all markers you wanted..."
        print "or type c to remove all previous points"
        a = raw_input()
        plt.gcf().canvas.mpl_disconnect(cid)
        if a == 'c':
            self.points = []

    def change_plotlim(self):
        print "LEFT WAVELENGTH (", self.pars['plotpars'][1][0], ")"
        ll = raw_input()
        if isfloat(ll) and ll != '':
            self.pars['plotpars'][1][0] = ll
        
        print "RIGHT WAVELENGTH (", self.pars['plotpars'][1][1], ")"
        rl = raw_input()
        if isfloat(rl) and rl != '':
            self.pars['plotpars'][1][1] = rl
        
        print "BOTTOM RELATIVE FLUX (", self.pars['plotpars'][1][2], ")"
        brf = raw_input()
        if isfloat(brf) and brf != '':
            self.pars['plotpars'][1][2] = brf
        
        print "TOP RELATIVE FLUX (", self.pars['plotpars'][1][3], ")"
        trf = raw_input()
        if isfloat(trf) and trf != '':
            self.pars['plotpars'][1][3] = trf

    ####################################################################
    # Change smoothing
    ####################################################################
    def smo_g(self):
        print "GIVE THE FWHM OF THE GAUSSIAN FUNCTION: [", \
            self.pars['plotpars'][3][1], ']'
        g = raw_input()
        if isfloat(g) is False:
            g = self.pars['plotpars'][3][1]  # keep the old value
        return g
            
    def smo_vrot(self):
        print "GIVE THE STELLAR vsini: [", self.pars['plotpars'][3][2], ']'
        v1 = raw_input()

        print "GIVE THE LIMB DARKENING COEFFICIENT:[", \
            self.pars['plotpars'][3][3], ']'
        v2 = raw_input()

        if isfloat(v1) is False or isfloat(v2) is False:
            v1 = self.pars['plotpars'][3][2]
            v2 = self.pars['plotpars'][3][3]
        return v1, v2

    def smo_vmac(self):
        print "GIVE THE MACROTURBULENT VELOCITY: [", self.pars['plotpars'][3][4], ']'
        m = raw_input()
        if isfloat(m) is False:
            m = self.pars['plotpars'][3][4]
        return m

    def smo_lntz(self):
        print "GIVE THE FWHM OF THE LORENTZIAN FUNCTION:[", \
            self.pars['plotpars'][3][5], ']'
        l_smooth = raw_input()
        if isfloat(l_smooth) is False:
            l_smooth = self.pars['plotpars'][3][5]
        return l_smooth
    
    def change_smoothing(self):
        print "  SMOOTHING: n=NONE, g=GAUSS, l=LORENZ, \
        v=ROTATION, m=MACROTURBULENCE\n \
                    c=v+g, d=m+g, r=m+v+g, p=VARIABLE GAUSS"
        smo = raw_input()

        if smo == 'n':
            self.pars['plotpars'][3] = ['n', '0.', '0.', '0.', '0.', '0.']
        elif smo == 'g':
            self.pars['plotpars'][3] = ['g', self.smo_g(), '0.', '0.', '0.', '0.']
        elif smo == 'v':
            v1, v2 = self.smo_vrot()
            self.pars['plotpars'][3] = ['v', '0.', v1, v2, '0.', '0.']
        elif smo == 'm':
            self.pars['plotpars'][3] = ['m', '0.', '0.', '0.', self.smo_vmac(), '0.']
        elif smo == 'l':
            self.pars['plotpars'][3] = ['m', '0.', '0.', '0.', '0.', self.smo_lntz()]
        elif smo == 'c':
            g = self.smo_g()
            v1, v2 = self.smo_vrot()
            self.pars['plotpars'][3] = ['c', g, v1, v2, '0.', '0.']
        elif smo == 'd':
            g = self.smo_g()
            m = self.smo_vmac()
            self.pars['plotpars'][3] = ['d', g, '0.', '0.', m, '0.']
        elif smo == 'r':
            g = self.smo_g()
            m = self.smo_vmac()
            v1, v2 = self.smo_vrot()
            self.pars['plotpars'][3] = ['r', g, v1, v2, m, '0.']

    ####################################################################
    # Apply shifts to observed spectrum
    ####################################################################

    def apply_shifts(self):
        # watch for double shifts!
        v_shift, w_shift, a_fac, m_fac = self.pars['plotpars'][2]
        print w_shift
        self.obs[:, 0] = self.obs[:, 0] + float(w_shift)
        l_shift = float(v_shift) / light_speed
        self.obs[:, 0] = self.obs[:, 0] * np.sqrt((1.0 + l_shift) / (1.0 - l_shift))
        self.obs[:, 1] = self.obs[:, 1] * float(m_fac) + float(a_fac)

    def find_multip_res(self, factor, d):
        yobs, model = d
        if self.flag == 'r':
            newf = yobs * factor
        elif self.flag == 'a':
            newf = yobs - factor
        return newf - model

    def find_multip(self):
        syntf = np.average(self.sflux[:, 1, :], axis=0)
        obsf = np.interp(self.sflux[0, 0], self.obs[:, 0], self.obs[:, 1])
        factor = so.leastsq(self.find_multip_res, [1.],
                            args=([obsf, syntf]), full_output=1)
        return round(factor[0][0], 2)
            
    def rescale_obs(self):
        if self.flag == 'r':
            print "MULTIPLY THE OBSERVED POINTS BY WHAT FACTOR?"
        else:
            print "ADD WHAT NUMBER TO THE OBSERVED POINTS?"
        print "press 'a' to find this factor automatically\n"
        rfactor = raw_input()

        if rfactor == 'a':
            rfactor = str(self.find_multip())
            print "%s %s" % ("Your new factor is:", rfactor)
            time.sleep(2.0)

        try:
            float(rfactor)
            if self.flag == 'r':
                self.pars['plotpars'][2][3] = rfactor
            elif self.flag == 'a':
                self.pars['plotpars'][2][2] = rfactor
        except ValueError:
            print "Your new value is not a number!"
            time.sleep(2.0)

        # Check if user uses additive and multiplicative shift at the same time
        if float(self.pars['plotpars'][2][2]) != 0.0 and self.flag == 'r':
            print "You cannot use additive shift and multiplicative\n \
            shift at the same time. Setting additive shift to 0"
            self.pars['plotpars'][2][2] = '0.0'
            print "Press enter to continue"
            raw_input()
            
        elif float(self.pars['plotpars'][2][3]) != 1.0 and self.flag == 'a':
            print self.pars['plotpars'][2]
            print "You cannot use additive shift and multiplicative\n \
            shift at the same time. Setting multipl. shift to 1"
            self.pars['plotpars'][2][3] = '1.0'
            print "Press enter to continue"
            raw_input()
       
    def v_shift(self):
        print "SHIFT THE OBSERVED POINTS BY WHAT VELOCITY (KM/S)?"
        rfactor = raw_input()
        self.pars['plotpars'][2][0] = rfactor
        # Check if w_fac is 0, if not - change it to 0
        if float(self.pars['plotpars'][2][1]) != 0.0:
            print "You cannot use wavelength shift and velocity\n \
            shift at the same time. Setting wavelength shift to 0"
            self.pars['plotpars'][2][1] = '0.0'
            print "Press any key to continue"
            raw_input()
    
    def w_shift(self):
        print "SHIFT THE OBSERVED POINTS BY WHAT WAVELENGTH?"
        rfactor = raw_input()
        self.pars['plotpars'][2][1] = rfactor
        # Check if v_fac is 0, if not - change it to 0
        if float(self.pars['plotpars'][2][0]) != 0.0:
            print "You cannot use wavelength shift and velocity\n \
            shift at the same time. Setting velocity shift to 0"
            self.pars['plotpars'][2][0] = '0.0'
            print "Press enter to continue"
            raw_input()
    
    ####################################################################
    # Add veil
    ####################################################################
    def add_veil(self):
        print "This option was created for pre Main-Sequence stars"
        print "Use it wisely! Setting veiling to 0.0 will remove \
        veiling from synthetic spectra. \n"

        print "WHAT IS THE ADDITIONAL FLUX IN TERMS OF CONTINUUM? [", \
            self.pars['veil'], "]"

        veil = raw_input()
        if isfloat(veil) is False:
            pass
        else:
            self.pars['veil'] = float(veil)
            
    ####################################################################
    # Change abundances and isotopes
    ####################################################################
    def change_abund(self):
        in_list = []
        
        if 'abundances' in self.pars.keys():
            for val in self.pars['abundances'][1:]:
                in_list.append(val[0])
            in_list = set(in_list)
            syn_no = int(self.pars['abundances'][0][1])
        else:
            in_list = set([])
            syn_no = 0
            self.pars['abundances'] = [['0', '0']]

        print "Which element to change?"
        a_id = raw_input()
        print "n = new abundances, or z = zero offsets?"
        flag = raw_input()     
    
        if flag == 'n':
            print "Enter the new offsets on the line below :"
            new = raw_input().split(None)
            if a_id in in_list:
                for index, val in enumerate(self.pars['abundances'][1:]):
                    if val[0] == a_id:
                        self.pars['abundances'][index+1][1][:syn_no] = new
            else:
                self.pars['abundances'].append([a_id, new])
   
        elif flag == 'z':
            for index, val in enumerate(self.pars['abundances'][1:]):
                if val[0] == a_id:
                    self.pars['abundances'].pop(index+1)
    
        self.pars['abundances'][0][0] = str(len(self.pars['abundances'][1:]))
        if self.pars['abundances'][0][1] == '0':
            self.pars['abundances'][0][1] = str(len(new))
    
    def change_isotopes(self):
        print "\nOptions: c = change an isotopic factor"
        print "         n = enter a new isotope "
        print "What is your choice?"
        flag = raw_input()

        if flag == 'c':
            print "Which isotope number from the list?"
            i_id = int(raw_input())
            print "What are the new division factors?"
            new = raw_input().split(None)
            self.pars['isotopes'][i_id][1] = new

        elif flag == 'n':  # add new entry to isotopes table
            print "What is the new isotope designation?"
            new_iso = raw_input()
                        
            print "What are its division factors?"

            new_fac = raw_input().split(None)
            
            if 'isotopes' not in self.pars.keys():
                self.pars['isotopes'] = [['0', str(len(new_fac))]]
                
            self.pars['isotopes'].append([new_iso, new_fac])
            self.pars['isotopes'][0][0] = str(len(self.pars['isotopes'][1:]))

    def change_syn_no(self):
        print "How many synths?"
        syn_no = raw_input()
        if 'abundances' in self.pars.keys():
            self.pars['abundances'][0][1] = syn_no
        if 'isotopes' in self.pars.keys():
            self.pars['isotopes'][0][1] = syn_no
       
    def abundances(self):
        iterate = True
        clear()
        while iterate:
            clear()
            print_driver(self.driver)

            print "element, abundance offsets OR isotope number, isotope name, factors"

            if 'abundances' in self.pars.keys():
                sno = int(self.pars['abundances'][0][1])
                for elem in enumerate(self.pars['abundances'][1:]):
                    print "%3s" % "", "%10s" % elem[1][0], \
                        ("".join("%10s " % ("%4.2f" % float(i)) for i in elem[1][1][:sno]))
                print ""
            
            if 'isotopes' in self.pars.keys():
                for i, elem in enumerate(self.pars['isotopes'][1:]):
                    print "%3i" % int(i+1), "%10s" % elem[0], \
                        ("".join("%10s " % ("%4.2f" % float(i)) for i in elem[1][:sno]))

            print "%10s %-25s %-25s" % \
                  ("\nOptions:", "c = change abundance", "i = change isotopic ratio")
            print "%10s %-25s %-25s %-10s" % \
                  ("", "n = change # syntheses", "q = rerun syntheses", "x = exit")
            print "What is your choice?"

            aopt = raw_input()

            if aopt == 'c':
                self.change_abund()
            elif aopt == 'n':
                self.change_syn_no()
            elif aopt == 'i':
                self.change_isotopes()
            elif aopt == 'q':  # rerun synthesis
                run_moog(self.driver, self.pars)
                iterate = False
            elif aopt == 'x':  # Forget all changes
                if 'abundances' in self.pars.keys():
                    self.pars['abundances'] = self.org_pars['abundances']
                if 'isotopes' in self.pars.keys():    
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
            try:
                for text in legend.get_texts():
                    text.set_color('k')
            except:
                pass
        for artist in plt.gca().get_children():
            if hasattr(artist, 'get_label') and artist.get_label() == '_line0':
                artist.set_color('k')

        if self.flag == 'f':
            print "Give the file name for the POSTSRIPT plot image:"
            tf = raw_input() + ".pdf"
        else:
            tf = "plot_"+id_generator() + ".pdf"
        
        plt.savefig(tf, facecolor='white', bbox_inches='tight', orientation='landscape')

    ####################################################################
    def run_synth(self):
        if self.obs_in_flag is True:
            self.apply_shifts()

        quit_moog = False
        while not quit_moog:
            self.do_plot()
            clear()
            
            print_driver(self.driver)
            if not self.obs_in_flag:
                print " !!! No observed spectrum provided"
                print " !!! Operations on observed spectrum are not active\n"

            self.print_options()

            self.flag = raw_input()
            if self.flag == 'q':
                quit_moog = True
            elif self.obs_in_flag and (self.flag == 'a' or self.flag == 'r'):
                self.rescale_obs()
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
                run_moog(self.driver, self.pars)
            elif self.flag == 'n':
                self.abundances()               
            elif self.flag == 'u':
                self.pars = copy.deepcopy(self.org_pars)
                self.xylim = map(float, self.pars['plotpars'][1])
                self.apply_shifts()
                run_moog(self.driver, self.pars)
            elif self.flag == 'l':
                self.add_veil()
            elif self.flag == 'p':
                self.set_cursor()
            elif self.flag == 'z':
                print "Use zoom button in plot window"
            elif self.flag == 'd':
                self.p2_flag = True
            elif self.flag == 't':
                print "Enter new title"
                self.pars['title'] = raw_input()
            elif self.flag == 'o':
                self.pars['plotpars'][1] = self.org_pars['plotpars'][1]
                self.xylim = map(float, self.pars['plotpars'][1])
                self.p2_flag = False
            else:
                print "Do not understand"
                time.sleep(0.5)

            plt.clf()
