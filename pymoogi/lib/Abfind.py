from Common_functions import *
import numpy as np
import matplotlib.pyplot as plt
from read_out_files import out2_abfind
import copy
import time


class AbfindPlot(object):

    def __init__(self, org_pars):
        self.fig, self.ax = plt.subplots(3)
        plt.subplots_adjust(hspace=0.5, right=0.9)
        self.org_pars = org_pars
        self.driver = 'abfind'

        self.data_orig = out2_abfind(org_pars['summary_out'][0][1:-1])  # data
        self.data = copy.deepcopy(self.data_orig)
        self.species_tab = np.array([])

        self.y = 'None'
        self.chosen_labels = []
    
    def choose_labels(self):
        print_driver(self.driver)
        labels = list(map(str, np.unique(np.array(self.data[:, 1], dtype=int))))
        print("Elements in your list:")
        print(labels)
        if len(labels) > 1:
            print("Choose element(s)")
            chosen_labels = input().split(" ")
            if chosen_labels[0] == 'q':
                exit()
        else:
            chosen_labels = labels
       
        for lbl in chosen_labels:
            if lbl not in labels:
                print("No data for atomic number", lbl)
                chosen_labels.remove(lbl)
               
        return chosen_labels
    
    def clear_axes(self):
        for iax in [0, 1, 2]:
            self.ax[iax].clear()
    
    def get_title(self):
        title = open(self.org_pars['summary_out'][0][1:-1]).readlines()[2].strip()
        return title
               
    def make_plot(self):
        colors = []
        for i, keyword in enumerate(np.unique(self.species_tab[:, 1])):
            elem_tab = self.species_tab[np.where(self.species_tab[:, 1] == keyword)]
            print_stats(elem_tab)
            for iax, ix in enumerate([2, 5, 0]):
                x = elem_tab[:, ix]
                y = elem_tab[:, 6]
                abplot = self.ax[iax].plot(x, y, 'o', label=keyword)
                color = abplot[0].get_color()
                self.ax[iax].axhline(np.average(y), color=color, ls='--')
                
                if len(y) > 3.:
                    a, b, c = do_stats(x, y)
                    self.ax[iax].plot(x, a * x + b, color=color)
            colors.append(color)
        
        legend = self.ax[0].legend(loc='lower center', bbox_to_anchor=(0.5, 1.00), ncol=5)
        for color, text in zip(colors, legend.get_texts()):
            text.set_color(color)        
            
        self.ax[0].set_xlabel("E.P. (eV)") 
        self.ax[1].set_xlabel("log (EW/lambda)")
        self.ax[2].set_xlabel("Lambda (A)")
        
        title = self.get_title()
        
        self.ax[1].text(.5, .8, title,
                        horizontalalignment='center',
                        transform=self.ax[1].transAxes, fontsize='smaller')
        
        ymin = self.species_tab[:, 6].min() - 0.5
        ymax = self.species_tab[:, 6].max() + 0.5
        
        for iax in [0, 1, 2]:
            self.ax[iax].set_ylabel("log eps")
            self.ax[iax].set_ylim(ymin, ymax)
        
    def update_plot(self):
        clear()
        # plt.gca().set_color_cycle('None')
        if not self.chosen_labels:
            print("Your list is empty")
        self.clear_axes()  
        clear()

        for lbl in self.chosen_labels:
            lab_tab = self.data[np.where(np.floor(self.data[:, 1]) == int(lbl))]
            if self.species_tab.shape[0] == 0:
                self.species_tab = lab_tab
            else:
                self.species_tab = np.append(self.species_tab, lab_tab, axis=0)
        self.make_plot()
        
        plt.draw()
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.click_on_plot)
           
    def click_on_plot(self, event):
        # Print x,y coords if user clicks on plot
        xcoord, ycoord = [event.xdata, event.ydata]
        r_ind = np.abs(ycoord - self.species_tab[:, 6]).argmin()
        self.species_tab = np.delete(self.species_tab, r_ind, 0)
        # for i in [0, 1, 2]:
        #    self.ax[i].set_color_cycle('None')
        self.clear_axes()
        self.make_plot()
        print("Switch [m]odel, change [v]t, [q]uit or any other key to plot")
    
    def switch_model(self, org_pars):
        old_model = self.org_pars['model_in']
        print("Name of file with new model of atmosphere?")
        new_model = input()
        self.org_pars['model_in'] = ["\'" + new_model + "\'"]
        try:
            run_moog(self.driver, self.org_pars)
        except:
            print("\n No such a file")
            org_pars['model_in'] = [old_model]
            time.sleep(1.5)
            
    def change_vt(self, vt):
        # Edit model
        model = open(self.org_pars['model_in'][0][1:-1]).readlines()
        vt_ind = 4 + int(re.search(r'\d+', model[2]).group())
        model[vt_ind] = "%9.2fE+05\n" % float(vt)
        # Write modified model to temporary file
        mout = open('temp.mod', 'w')
        for item in model:
            mout.write(item)
        mout.close()
        self.org_pars['model_in'] = ['\'temp.mod\'']
        run_moog('abfind', self.org_pars)
           
    def run(self):
        plot_again = ''
        # self.data=out2_ab(self.org_pars['summary_out'][0][1:-1])
        while plot_again != 'q':
            self.chosen_labels = self.choose_labels()
            self.update_plot()            
            plt.show()
            print("Switch [m]odel, change [v]t, [q]uit or any other key to plot again")
            plot_again = input()
            if plot_again == 'm':
                self.switch_model(self.org_pars)
                self.data = out2_abfind(self.org_pars['summary_out'][0][1:-1])
            elif plot_again == 'v':
                print("What is the new microturbulence (km/s)?")
                vt = input()
                
                self.change_vt(vt)
                self.data = out2_abfind(self.org_pars['summary_out'][0][1:-1])

            self.species_tab = np.array([])
            clear()
