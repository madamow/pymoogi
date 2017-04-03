import os,re,sys
required = ['numpy', 'scipy', 'matplotlib']
for package in required:
	try:
		exec('import {}'.format(package))
	except ImportError:
		print('\nYou need to install the package "{}"'.format(package))
		exit()

#Check if you have enviromental variable "MOOGPATH"
try: 
    MOOG_HOME = os.environ['MOOGPATH']
    print "MOOGPATH =",MOOG_HOME
except KeyError:
    print "MOOGPATH not found"
    print "Export MOOG path"
    exit()


#Check if you have executable MOOG file exists
if os.path.isfile(os.path.join(MOOG_HOME,"MOOG")):
    print "MOOG is ready"
else:
    print "Compile MOOG"
    exit()

import time, copy
import random, string
import numpy as np
import subprocess as sp
import matplotlib.pyplot as plt
import scipy.constants as sc
import scipy.stats as ss
import scipy.optimize as so
import matplotlib
from elements import ELEMENTS
from matplotlib import rcParams
from matplotlib import ticker

plt.switch_backend('qt5Agg')

light_speed = sc.c * 0.001

#######SM style for matplotlib
def SM_style():
    #lines
    matplotlib.rc('figure', facecolor ='black')

    rcParams['lines.linewidth']  = 2.0
    rcParams['lines.linestyle']  = '-'
    rcParams['lines.color']      = 'white'

    #fonts & text
    rcParams['font.family']      =   'serif'
    rcParams['font.weight']      =   'normal'
    rcParams['font.size']        =   12.0
    rcParams['text.color']       =   'white'

    #axes & ticks
    rcParams['axes.edgecolor']   =    'white'
    rcParams['axes.facecolor']   =    'black'
    rcParams['axes.linewidth']   =    1.0
    rcParams['axes.grid']        =    False
    rcParams['axes.titlesize']   =    'large'
    rcParams['axes.labelsize']   =    'large'
    rcParams['axes.labelcolor']  =    'white'

    rcParams['xtick.major.size'] =     7
    rcParams['xtick.minor.size'] =     4
    rcParams['xtick.major.pad']  =     6
    rcParams['xtick.minor.pad']  =     6
    rcParams['xtick.labelsize']  =     'large'
    rcParams['xtick.minor.width']=     1.0
    rcParams['xtick.major.width']=     1.0

    rcParams['ytick.major.size'] =     7
    rcParams['ytick.minor.size'] =     4
    rcParams['ytick.major.pad']  =     6
    rcParams['ytick.minor.pad']  =     6
    rcParams['ytick.labelsize']  =     'large'
    rcParams['ytick.minor.width']=     1.0
    rcParams['ytick.major.width']=     1.0

    rcParams['xtick.color']  =    'white'
    rcParams['ytick.color']  =    'white'

    #legends
    rcParams['legend.numpoints']=      1
    rcParams['legend.fontsize'] =      'large'
    rcParams['legend.shadow']   =      False
    rcParams['legend.frameon']  =      False

def getKey(item):
    return item[0]

def isfloat(value):
  #Check if value can be float
  try:
      float(value)
      return True
  except ValueError:
      return False

def str_to_list(s):
    #Write long str as a list
    #divide long string, get lines without spaces
    lines= s.split('\n')
    tab=[]
    driver = lines[0]
    for line in lines[1:]:
    #Remove unneccesary spaces
        l_list = filter(None,  line.split(" "))
        tab.append(l_list)

    return driver,filter(None,tab)


def list_to_dict(sf):
    driver, tab=str_to_list(sf)
    smoothing_types = ['g','l','v','m','c','d','r']
    l_par = set(['isotopes','abundances','plotpars','synlimits'])

    #Transform list to dict
    dict={}
    for line in tab:
       if not isfloat(line[0]) and smoothing_types.count(line[0])==0:
          if not line[0] in l_par:
              dict[line[0]] = []
              dict[line[0]].append(line[1])
          else:
              dict[line[0]] = []
              ind=tab.index(line)

              if line[0]=='abundances' or line[0]=='isotopes':
                  dict[line[0]].append([line[1],line[2]])
                  iline= np.arange(ind+1, 1+ind+int(line[1]))
                  for i in iline:
                      dict[line[0]].append([tab[i][0],tab[i][1:]])
              elif line[0]=='synlimits':
                  dict[line[0]].append(tab[ind+1])
              elif line[0]=='plotpars':
                  if line[1]=='1':
                      iline= np.arange(ind+1, ind+4)
                      dict[line[0]].append(1)
                      for i in iline:
                          dict[line[0]].append(tab[i])
                  else:
                       dict[line[0]].append(0)
    try:
        dict['abundances'][1:]=sorted(dict['abundances'][1:], key=getKey)
    except KeyError:
        pass
    try:
        dict['isotopes'][1:]=sorted(dict['isotopes'][1:], key=getKey)
    except KeyError:
        pass
    return driver,dict

##Recreate back proper string
def dict_to_str(driver,dict):
    s=driver+"\n"
    keys=['standard_out','summary_out','smoothed_out','model_in',
          'lines_in','strong','stronglines_in','freeform','opacit',
          'observed_in','atmosphere',
          'trudamp','units','lines','molecules',
          'flux/int ','fluxlimits','coglimits','blenlimits',
          'obspectrum','iraf','damping','plot','histogram']

    for elem in keys:
        if elem in dict.keys():
            s=s+elem+" "+str(dict[elem][0])+"\n"

    if 'abundances' in dict.keys():
        sno=int(dict['abundances'][0][1])
        s=s+"abundances "+dict['abundances'][0][0]+" "+dict['abundances'][0][1]+"\n"
        for line in dict['abundances'][1:]:
            s=s+"    "+line[0]+"    "
            s=s+(' '.join(line[1][:sno]))+"\n"

    if 'isotopes' in dict.keys():
        s=s+"isotopes "+dict['isotopes'][0][0]+" "+dict['isotopes'][0][1]+"\n"
        for line in dict['isotopes'][1:]:
            s=s+"    "+line[0]+"    "
            s=s+(' '.join(line[1][:sno]))+"\n"

    if 'synlimits' in dict.keys():
        s=s+"synlimits\n"
        s=s+"    "+' '.join(dict['synlimits'][0])+"\n"

    if 'plotpars' in dict.keys():
        s=s+"plotpars"+" "+str(dict['plotpars'][0])+"\n"
        for line in dict['plotpars'][1:]:
            s=s+(' '.join(line))+"\n"

    if 'obspectrum' in dict.keys():
        s=s+"obspectrum "+dict['obspectrum'][0]+"\n"

    return s

def run_moog(driver,pars):
    st=dict_to_str(driver,pars)

    with open('./batch.par', 'w') as batchpar:
        batchpar.write(st)
    sp.check_output('echo "batch.par\nq" | %s/MOOG' % MOOG_HOME, shell=True)

def print_driver(driver):
    print "****************************************************************************"
    print "MOOG IS CONTROLLED BY DRIVER", driver
    print "****************************************************************************\n"

def id_generator(size=3, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

##############################################
#Synth module
##############################################

class SynthPlot(object):

    def __init__(self, org_pars):
        self.pars = copy.deepcopy(org_pars)
        self.org_pars = org_pars
        self.p2_flag = False
        self.flag = ''
        self.obs=np.loadtxt(self.pars['observed_in'][0][1:-1])
        self.points = []
        self.xylim = map(float,self.pars['plotpars'][1])        

    def print_options(self):
        print "OPTIONS?    s=new smoothing     r=rescale obs."
        print "            a=add # to obs.     h=hardcopy"
        print "            c=change bounds     q=quit"
        print "            m=redo same plot    o=orig. plot bounds"
        print "            v=velocity shift    w=wavelength shift "
        print "            z=use zoom button  p=cursor position"
        print "            t=change title      f=postscript file "
        print "            n=new abundances    d=obs/syn deviation"
        print "            l=add veiling       u=undo all; replot"
        print "\nWhat is your choice? "


##done and checked
    def out2_reader(self,file):
        #split into blocks
        with open(file, 'r') as fh:
            data_all = fh.read().split("ALL")
        #first element is always empty, remove it
        data_all.pop(0)

        out2_tab=[]
        header_line =np.zeros((1,4))

        # Find line that matches format header_line
        for data in data_all:
            ax=[]
            isotopes=[]
            flux=[]

            for line in filter(None, data.split("\n")):
                line_list  = line.split()
                #Find values for x axis
                try:
                    np.array(line_list,dtype=float)
                    if len(line_list)>1:
                        header_line[:]=np.array(line_list,dtype=float)
                        head = np.array(line_list,dtype=float)
                        break  # exit with first line found
                except:
                    pass

                #Find model
                if line_list[0] =='MODEL:':
                    model = " ".join(line.split(":")[1].split())

                #Find abundances
                if line_list[0]=='element':
                    el= line.strip().split(":")[0].strip().split(" ")[-1]
                    ab= line.strip().split(":")[1].strip().split(" ")[-1]
                    ax.append([el, ab])
                #Find isotopes
                if line_list[0]=='Isotopic':
                    isot =  line.strip().split(":")[1].strip().split("=")[0].strip()
                    ratio= line.strip().split(":")[1].strip().split("=")[-1].strip()
                    isotopes.append([isot, ratio])

            for line in  filter(None, data.split("\n")):
                line_list  = line.split()
                #Find all lines that match format data_line
                try:
                    flux.append(np.array(line_list,dtype=float))
                except:
                    pass

            # remove first element of the list
            flux.pop(0)

            # flatten list of lists
            # http://stackoverflow.com/questions/952914/
            flux = [item for sublist in flux for item in sublist]
            dline=(head,model,ax,isotopes,1.-np.array(flux))
            out2_tab.append(dline)
        return out2_tab

    def out3_reader(self,file):
    # like out2
        with open(file, 'r') as fh:
            data_all = fh.read().split("the number of")
        data_all.pop(0)

        tab_out3=[]

        for data in data_all:
            flux = []
            for line in filter(None,data.split("\n")):
                line_list=line.split()
                try:
                    np.array(line_list,dtype=float)
                    flux.append(line_list)
                except:
                    pass

            x= np.asarray(flux)[:,0]
            y= np.asarray(flux)[:,1]
            tab_out3.append((x,y))

        return tab_out3
    
    def ax_plot(self):
        #some basic formatting on plot
        self.ax.plot(self.lam,self.flux,'o',color= rcParams['lines.color'])
        self.ax.set_xlim(self.xylim[0],self.xylim[1])
        self.ax.set_ylim(self.xylim[2],self.xylim[3])

        #Plot syntetic spectra
        colors=[]
        for i,line in enumerate(self.sflux):
            ssp = self.ax.plot(line[0],line[1],label=self.labels[i])
            colors.append(ssp[0].get_color())
        
        #Create legend
        try:
            legend = self.ax.legend(loc=3,frameon=False)
            for color,text in zip(colors,legend.get_texts()):
                text.set_color(color)
        except AttributeError:
            pass
    
    
    def bx_plot(self):
    #Plot O-C on second panel
        #bx.xaxis.set_minor_locator( ticker.AutoMinorLocator() )
        yoc=np.interp(self.sflux[0][0],self.lam,self.flux)
    
        colors=[]
        for spec in self.sflux:
            l=self.bx.plot(spec[0],yoc-spec[1],
                           label=round(np.std(yoc-spec[1],ddof=1),4))
            colors.append(l[0].get_color())
        self.bx.axhline(0.,ls='dotted',color='r')
    
        #Set legend
        legend = self.bx.legend(loc=3,frameon=False)
        for color,text in zip(colors,legend.get_texts()):
            text.set_color(color)
    
        
        
    def isotope_labels(self):
        s='Isotopes:\n'
        for item in self.pars['isotopes'][1:]:
             s=s+item[0]+": "+"/".join(item[1])+"\n"
        return s

    
    def draw_marker(self,x,y):
        lbl=str(round(x,2))+"\n"+str(round(y,2))

        plt.annotate(lbl, xy=(x, y),  xycoords='data',
                    arrowprops=dict(arrowstyle='->',color='r'),
                    xytext=(x, y-0.15), fontsize=10, textcoords='data',
                    horizontalalignment='center', verticalalignment='top',
                    )
    
    def mark_points(self,event):
        #Put an arrow with x,y coords if user clicks on plot
        self.draw_marker(event.xdata,event.ydata)
        self.points.append([event.xdata,event.ydata])
        
        
    def on_xlims_change(self,axes):
        self.xylim[0],self.xylim[1] = axes.get_xlim()
    def on_ylims_change(self,axes):
        self.xylim[2],self.xylim[3] = axes.get_ylim()

    
    def do_plot(self):
        self.out2=self.out2_reader(self.pars['summary_out'][0][1:-1])
        self.out3=self.out3_reader(self.pars['smoothed_out'][0][1:-1])
        self.sflux=np.array(copy.deepcopy(self.out3),dtype=float)
        
        #Create labels
        self.labels=[]
        for i,spec in enumerate(self.sflux):
            s=''
            for l in self.out2[i][2]:
                s=s+l[0]+"="+l[1]+" "
            self.labels.append(s.strip())
            
            if self.pars['veil'] > 0.0:
                veil=float(self.pars['veil'])
                self.sflux[i,1,:] = (spec[1]+veil)/(1.+veil)
            
        if self.p2_flag == True:
            self.ax = plt.subplot2grid((2,1),(0,0))
            self.bx = plt.subplot2grid((2,1),(1,0),sharex=self.ax)
            self.ax_plot()

            self.bx_plot()
            plt.setp(self.ax.get_xticklabels(),visible=False)
            plt.subplots_adjust(hspace=0.)
            
            self.bx.set_xlabel('Wavelength')
            self.bx.set_ylabel('Obs - comp')
        
        else:
            self.ax = plt.subplot2grid((1,1),(0,0))
            self.ax_plot()
            self.ax.set_xlabel('Wavelength')
        
        self.ax.set_ylabel('Rel. flux')
        self.ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        self.ax.xaxis.set_minor_locator( ticker.AutoMinorLocator() )
        self.ax.yaxis.set_minor_locator( ticker.AutoMinorLocator() )
        x_formatter = ticker.ScalarFormatter(useOffset=False)
        self.ax.xaxis.set_major_formatter(x_formatter)
        
        #Set title
        if self.pars['title']=="":
            title_obj = self.ax.set_title(self.out2[0][1])
        else:
            title_obj = self.ax.set_title(self.pars['title'])

        #Print input files' names
        files_info = self.pars['observed_in'][0]+"\n"+\
        self.pars['lines_in'][0]+"\n"+self.pars['model_in'][0]+"\n"        
        #Set smoothing info:
        smo_info = "smoothing: "+str(self.pars['plotpars'][3][0])+" = "
        smo_nr = filter(lambda x: float(x) != 0,self.pars['plotpars'][3][1:])
        for item in smo_nr:
            smo_info=smo_info+item+", "

        extra_info = files_info+smo_info+"\n"    
    

        #Set isotopes labels
        if 'isotopes' in self.pars.keys():
            iso_txt=self.isotope_labels()+"\n"
            extra_info=extra_info+iso_txt

        self.ax.text(0.99,0.01,extra_info,
            horizontalalignment='right',
            verticalalignment='bottom',
            transform=self.ax.transAxes)

        #Draw markers
        if len(self.points) !=0:
            for x,y in self.points:
                self.draw_marker(x,y)
                
        plt.sca(self.ax)
        self.ax.callbacks.connect('xlim_changed', self.on_xlims_change)
        self.ax.callbacks.connect('ylim_changed', self.on_ylims_change)  
        
    def set_cursor(self):
        cid=plt.gcf().canvas.mpl_connect('button_press_event',
                                             self.mark_points)
        print "Click on the plot window to mark a point(s)"
        print "and press enter when you get all markers you wanted..."
        print "or type c to remove all previous points"
        a = raw_input()
        plt.gcf().canvas.mpl_disconnect(cid)
        if  a =='c':
            self.points=[]


    def change_plotlim(self):
        print "LEFT WAVELENGTH (",self.pars['plotpars'][1][0],")"
        ll=raw_input()
        if isfloat(ll) == True and ll != '':
            self.pars['plotpars'][1][0]=ll
        print "RIGHT WAVELENGTH (",self.pars['plotpars'][1][1],")"
        rl=raw_input()
        if isfloat(rl) == True and rl != '':
           self.pars['plotpars'][1][1]=rl
        print "BOTTOM RELATIVE FLUX (",self.pars['plotpars'][1][2],")"
        brf=raw_input()
        if isfloat(brf) == True and brf != '':
            self.pars['plotpars'][1][2]=brf
        print "TOP RELATIVE FLUX (",self.pars['plotpars'][1][3],")"
        trf=raw_input()
        if isfloat(trf) == True and trf != '':
            self.pars['plotpars'][1][3]=trf

    ####################################################################
    #Change smoothing
    ####################################################################
    def smo_g(self):
        print "GIVE THE FWHM OF THE GAUSSIAN FUNCTION: [",\
        self.pars['plotpars'][3][1],']'
        g=raw_input()
        if isfloat(g) == False:
            g = self.pars['plotpars'][3][1] #keep the old value
        return g
            
    def smo_vrot(self):
        print "GIVE THE STELLAR vsini: [",self.pars['plotpars'][3][2],']'
        v1=raw_input()

        print "GIVE THE LIMB DARKENING COEFFICIENT:[",\
        self.pars['plotpars'][3][3],']'
        v2=raw_input()

        if isfloat(v1) == False or isfloat(v2) == False:
            v1 = self.pars['plotpars'][3][2]
            v2 = self.pars['plotpars'][3][3]
        return v1,v2

    def smo_vmac(self):
        print "GIVE THE MACROTURBULENT VELOCITY: [",self.pars['plotpars'][3][4],']'
        m=raw_input()
        if isfloat(m) == False:
            m = self.pars['plotpars'][3][4]
        return m

    def smo_lntz(self):
        print "GIVE THE FWHM OF THE LORENTZIAN FUNCTION:[",\
        self.pars['plotpars'][3][5],']'
        l=raw_input()
        if isfloat(l) == False:
            l = self.pars['plotpars'][3][5]
        return l
    
    def change_smoothing(self):
        print "  SMOOTHING: n=NONE, g=GAUSS, l=LORENZ, \
        v=ROTATION, m=MACROTURBULENCE\n \
                    c=v+g, d=m+g, r=m+v+g, p=VARIABLE GAUSS"
        smo=raw_input()

        if smo == 'n':
            self.pars['plotpars'][3]=['n','0.','0.','0.','0.','0.']
        elif smo == 'g':
           self.pars['plotpars'][3]=['g',self.smo_g(),'0.','0.','0.','0.']
        elif smo == 'v':
            v1,v2=self.smo_vrot()
            self.pars['plotpars'][3]=['v','0.',v1,v2,'0.','0.']
        elif smo == 'm':
            self.pars['plotpars'][3]=['m','0.','0.','0.',self.smo_vmac(),'0.']
        elif smo == 'l':
            self.pars['plotpars'][3]=['m','0.','0.','0.','0.',self.smo_lntz()] 
        elif smo == 'c' :
            g = self.smo_g()
            v1,v2=  self.smo_vrot()
            self.pars['plotpars'][3]=['c',g,v1,v2,'0.','0.']
        elif smo == 'd' :
            g = self.smo_g()
            m = self.smo_vmac()
            self.pars['plotpars'][3]=['d',g,'0.','0.',m,'0.']
        elif smo == 'r' :
            g = self.smo_g()
            m = self.smo_vmac()
            v1,v2 = self.smo_vrot()
            self.pars['plotpars'][3]=['r',g,v1,v2,m,'0.']
    
    
    ####################################################################
    #Apply shifts to observed spectrum
    ####################################################################

    def apply_shifts(self):
        #watch for double shifts!
        v_shift,w_shift,a_fac,m_fac=self.pars['plotpars'][2]
        self.lam = self.obs[:,0]+float(w_shift)
        l_shift = float(v_shift) / light_speed
        self.lam = self.lam * np.sqrt((1.0 + l_shift) / (1.0 - l_shift))
        self.flux = self.obs[:,1]*float(m_fac)+float(a_fac)
    
    def find_multip_res(self,p,d):
        factor=p
        yobs,model=d
        if self.flag=='r':
            newf=yobs*factor
        elif self.flag=='a':
            newf=yobs-factor
        return (newf - model)

    def find_multip(self):
        syntf=np.average(self.sflux[:,1,:],axis=0)
        obsf=np.interp(self.sflux[0,0],self.obs[:,0],self.obs[:,1])
        factor = so.leastsq(self.find_multip_res,[1.],
                         args=([obsf,syntf]),
                         full_output=1)
        return round(factor[0][0],2)
            
    def rescale_obs(self):
        if self.flag=='r':
            print "MULTIPLY THE OBSERVED POINTS BY WHAT FACTOR?"
        else:
            print "ADD WHAT NUMBER TO THE OBSERVED POINTS?"
        print "press 'a' to find this factor automatically\n"
        rfactor=raw_input()

        if rfactor =='a':
            rfactor=str(self.find_multip())
            print "%s %s" % ("Your new factor is:", rfactor)
            time.sleep(2.0)

        try:
           float(rfactor)
           if self.flag == 'r':
               self.pars['plotpars'][2][3]=rfactor
           elif self.flag == 'a':
               self.pars['plotpars'][2][2]=rfactor
        except ValueError:
            print "Your new value is not a number!"
            time.sleep(2.0)

        #Check if user uses additive and multiplicative shift at the same time
        if float(self.pars['plotpars'][2][2]) != 0.0 and self.flag=='r':
            print "You cannot use additive shift and multiplicative\n \
            shift at the same time. Setting additive shift to 0"
            self.pars['plotpars'][2][2]='0.0'
            print "Press enter to continue"
            raw_input()
            
        elif float(self.pars['plotpars'][2][3]) != 1.0 and self.flag=='a':
            print self.pars['plotpars'][2]
            print "You cannot use additive shift and multiplicative\n \
            shift at the same time. Setting multipl. shift to 1"
            self.pars['plotpars'][2][3]='1.0'
            print "Press enter to continue"
            raw_input()
       
    def v_shift(self):
        print "SHIFT THE OBSERVED POINTS BY WHAT VELOCITY (KM/S)?"
        rfactor = raw_input()
        self.pars['plotpars'][2][0] = rfactor
        #Check if w_fac is 0, if not - change it to 0
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
        #Check if v_fac is 0, if not - change it to 0
        if float(self.pars['plotpars'][2][0]) != 0.0:
            print "You cannot use wavelength shift and velocity\n \
            shift at the same time. Setting velocity shift to 0"
            self.pars['plotpars'][2][0]='0.0'
            print "Press enter to continue"
            raw_input()
    
    ####################################################################
    #Add veil
    ####################################################################
    def add_veil(self):
        print "This option was created for pre Main-Sequence stars"
        print "Use it wisely! Setting veiling to 0.0 will remove \
        veiling from synthetic spectra. \n"

        print "WHAT IS THE ADDITIONAL FLUX IN TERMS OF CONTINUUM? [",\
        self.pars['veil'],"]"

        veil = raw_input()
        if isfloat(veil) == False:
            pass
        else:
            self.pars['veil'] = float(veil)
            
    ####################################################################
    #Change abundances and isotopes
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
            syn_no=0
            self.pars['abundances']=[['0','0']]

        print "Which element to change?"
        a_id = raw_input()
        print "n = new abundances, or z = zero offsets?"
        flag = raw_input()     
    
        if flag == 'n':
            print "Enter the new offsets on the line below :"
            new=raw_input().split(None)
            if a_id in in_list:
                for index, val in enumerate(self.pars['abundances'][1:]):
                    if val[0] == a_id:
                        self.pars['abundances'][index+1][1][:syn_no] = new
            else:
                self.pars['abundances'].append([a_id,new])
   
        elif flag == 'z':
            for index, val in enumerate(self.pars['abundances'][1:]):
                if val[0] == a_id:
                    self.pars['abundances'].pop(index+1)
    
        self.pars['abundances'][0][0] = str(len(self.pars['abundances'][1:]))
        if self.pars['abundances'][0][1]=='0': 
            self.pars['abundances'][0][1] = str(len(new))
    
    def change_isotopes(self):
        print "\nOptions: c = change an isotopic factor"
        print "         n = enter a new isotope "
        print "What is your choice?"
        flag = raw_input()
        

        if flag == 'c':
            print self.pars['isotopes']
            print "Which isotope number from the list?"
            i_id = int(raw_input())
            print "What are the new division factors?"
            new=raw_input().split(None)
            self.pars['isotopes'][i_id][1]=new

        elif flag == 'n': #add new entry to isotopes table
            print "What is the new isotope designation?"
            new_iso = raw_input()
                        
            print "What are its division factors?"

            new_fac = raw_input().split(None)
            
            if 'isotopes' not in self.pars.keys():
                self.pars['isotopes']=[['0',str(len(new_fac))]]
                
            self.pars['isotopes'].append([new_iso,new_fac])
            self.pars['isotopes'][0][0]=str(len(self.pars['isotopes'][1:]))
            
    
    def change_syn_no(self):
        print "How many synths?"
        syn_no = raw_input()
        if 'abundances' in self.pars.keys():
            self.pars['abundances'][0][1]=syn_no
        if 'isotopes' in self.pars.keys():
            self.pars['isotopes'][0][1]=syn_no
    
    
    def abundances(self):
        iterate=True
        clear()
        while iterate:
            clear()
            print_driver(driver)

            print "element, abundance offsets OR isotope number, isotope name, factors"

            if 'abundances' in self.pars.keys():
                sno=int(self.pars['abundances'][0][1])
                for elem in self.pars['abundances'][1:]:
                    print "%3s" %  "","%10s" % elem[0],\
                    ("".join("%10s "% ("%4.3f"% float(i)) 
                    for i in elem[1][:sno] ) )
                print ""
            
            if 'isotopes' in self.pars.keys():
                for i,elem in  enumerate(self.pars['isotopes'][1:]):
                    print "%3i" % int(i+1), "%10s" % elem[0],\
                    ("".join("%10s "% ("%4.3f"% float(i)) 
                    for i in elem[1][:sno] ) )

            print "%10s %-25s %-25s" % \
            ("\nOptions:","c = change abundance","i = change isotopic ratio")
            print "%10s %-25s %-25s %-10s" % \
            ("","n = change # syntheses","q = rerun syntheses","x = exit")
            print "What is your choice?"

            aopt=raw_input()

            if aopt == 'c':
                self.change_abund()
            elif aopt == 'n':
                self.change_syn_no()
            elif aopt == 'i':
                self.change_isotopes()
            elif aopt == 'q': #rerun synthesis
                iterate = False
            elif aopt == 'x': #Forget all changes
                if 'abundances' in self.pars.keys():
                    self.pars['abundances'] = self.org_pars['abundances']
                if 'isotopes' in self.pars.keys():    
                    self.pars['isotopes'] = self.org_pars['isotopes']
                iterate = False
    
    
    ####################################################################
    #Create hardcopy of plot
    ####################################################################
    def hardcopy(self):
        for ax in fig.axes:
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
            l= ax.get_legend()
            try:
                for text in l.get_texts():
                    text.set_color('k')
            except:
                pass
        for artist in plt.gca().get_children():
            if hasattr(artist,'get_label') and artist.get_label()=='_line0':
                artist.set_color('k')

        if self.flag == 'f':
            print "Give the file name for the POSTSRIPT plot image:"
            tf=raw_input()+".pdf"
        else:
            tf="plot_"+id_generator()+".pdf"
        plt.savefig(tf, facecolor='white', 
                    bbox_inches='tight',orientation='landscape')
    
    
    ####################################################################
    def run_synth(self):
        self.apply_shifts()
        
        quit = False
        while  quit==False:
            self.do_plot()
            clear()

            print_driver(driver)
            self.print_options()

            self.flag=raw_input()
            if self.flag ==   'q' :
                quit=True
            elif self.flag == 'a' or self.flag == 'r':
                self.rescale_obs()
                self.apply_shifts()
            elif self.flag == 'w' :
                self.w_shift()
                self.apply_shifts()
            elif self.flag == 'v' :
                self.v_shift()
                self.apply_shifts()
            elif self.flag == 'h' or self.flag == 'f':
                self.hardcopy()
            elif self.flag == 'c' :
                self.change_plotlim()
            elif self.flag == "m" :
                self.do_plot()
            elif self.flag == 's' :
                self.change_smoothing()
                run_moog(driver,self.pars)
            elif self.flag == 'n' :
                self.abundances()
                run_moog(driver,self.pars)
            elif self.flag == 'u':
                self.pars=copy.deepcopy(self.org_pars)
                self.xylim = map(float,self.pars['plotpars'][1])        
                self.apply_shifts()
                run_moog(driver,self.pars)
            elif self.flag == 'l':
                self.add_veil()
            elif self.flag == 'p':
                self.set_cursor()
            elif self.flag == 'z':
               print "Use zoom button in plot window"
            elif self.flag == 'd':
                self.p2_flag=True
            elif self.flag == 't':
                print "Enter new title"
                self.pars['title'] = raw_input()
            elif self.flag == 'o':
                self.pars['plotpars'][1]=self.org_pars['plotpars'][1]
                self.xylim = map(float,self.pars['plotpars'][1])        
                self.p2_flag=False
            else:
                print "Do not understand"
                time.sleep(0.5)

            plt.clf()
        
##################################
##################################
#Abfind driver
##################################
def out2_ab(file):
    # read filename from commandline
    with open(file, 'r') as fh:
        data = fh.readlines()

    line_data=np.zeros((1,8),dtype=float)

    for line in data:
        line=re.split('\s+',line.strip())

        try:
            line=np.array(line,dtype=float)
            line_data=np.append(line_data,np.array([line]),axis=0)
        except:
            pass

    return line_data[1:,:]
 
def do_stats(x,y):
    a,b=np.polyfit(x,y,1)
    c=ss.pearsonr(x,y)[0]
    return a,b,c

def set_color_cycle(self, clist=None):
    if clist is 'None':
        clist = rcParams['axes.color_cycle']
    self.color_cycle = itertools.cycle(clist)

class ABPlot(object):

    def set_color_cycle(self, clist=None):
        if clist is None:
            clist = rcParams['axes.color_cycle']
        self.color_cycle = itertools.cycle(clist)
    
    def __init__(self, org_pars, ax):
        self.data_orig = out2_ab(org_pars['summary_out'][0][1:-1])# data
        self.data = out2_ab(org_pars['summary_out'][0][1:-1])
        self.species_tab = np.array([])
        self.ax = ax
        self.y='None'
        self.chosen_labels=[]
        
    def print_stats(self,t):
        print "Here are abundances for",ELEMENTS[int(t[0,1])]
        print "%10s %5s %8s %8s %8s %7s %7s %8s" % \
             ("wavelength","ID","EP","logGF","EWin","logRWin","abund","delavg")
        for l in t[t[:,0].argsort()]:
            print "%10.2f %5.1f %8.2f %8.2f %7.2f %7.3f %8.3f %8.3f" % \
                  (l[0],l[1],l[2],l[3],l[4],l[5],l[6],l[7])
        if t.shape[0]==1.:
            print "Just one line, no stats"
        else:
            print "average abundance  = %-9.3f std. deviation =  %-9.3f #lines = %3i" % \
              (np.average(t[:, 6]),np.std(t[:, 6],ddof=1),len(t[:, 6]))
        if t.shape[0]>3.:
            print "E.P. correlation:  slope = %7.3f  intercept = %7.3f  corr. coeff. = %7.3f" %\
                (do_stats(t[:,2],t[:, 6]))
            print "R.W. correlation:  slope = %7.3f  intercept = %7.3f  corr. coeff. = %7.3f" %\
                (do_stats(t[:,5],t[:, 6]))
            print "wav. correl.:  slope = %7.3e  intercept = %7.3f  corr. coeff. = %7.3f\n" %\
                (do_stats(t[:,0],t[:, 6]))
        else:
            print "No statistics done for E.P. trends"
            print "No statistics done for R.W. trends"
            print "No statistics done for wav. trends\n"
    
    def choose_labels(self):
        print_driver(driver)
        labels= map(str, np.unique(np.array(self.data[:,1],dtype=int)))
        print "Elements in your list:"
        print labels
        if len(labels)>1:
            print "Choose element(s)"
            chosen_labels =raw_input().split(" ")
            if chosen_labels[0]=='q':
                exit()
        else:
            chosen_labels=labels
       
        for lbl in chosen_labels:
            if not lbl in labels:
               "No data for atomic number",lbl
               chosen_labels.remove(lbl) 
               
        return chosen_labels
    
    def clear_axes(self):
        for iax in [0,1,2]:
             self.ax[iax].clear() 
    
    def get_title(self):
        title=open(org_pars['summary_out'][0][1:-1]).readlines()[2].strip()
        return title
        
          
    def make_plot(self):
        colors=[]
        for i,keyword in enumerate(np.unique(self.species_tab[:,1])):
            elem_tab = self.species_tab[np.where
            (self.species_tab[:,1]==keyword)]
            self.print_stats(elem_tab)
            for iax, ix in enumerate([2,5,0]):
                x=elem_tab[:,ix]
                y=elem_tab[:,6]
                abplot=self.ax[iax].plot(x, y, 'o',label=keyword)
                color=abplot[0].get_color()
                self.ax[iax].axhline(np.average(y),color=color,ls='--')
                
                if len(y)>3.:
                   a,b,c=do_stats(x,y)
                   self.ax[iax].plot(x,a*x+b,color=color)
            colors.append(color)
        
        legend=self.ax[0].legend(loc='lower center', bbox_to_anchor=(0.5, 1.00),
                  ncol=5)
        for color,text in zip(colors,legend.get_texts()):
            text.set_color(color)        
            
        ax[0].set_xlabel("E.P. (eV)") 
        ax[1].set_xlabel("log (EW/lambda)")
        ax[2].set_xlabel("Lambda (A)")
        
        title=self.get_title()
        
        ax[1].text(.5,.8,title,
        horizontalalignment='center',
        transform=ax[1].transAxes,fontsize='smaller')
        
        for iax in [0,1,2]:
           ax[iax].set_ylabel("log eps")
        
    def update_plot(self):
        clear()
        colors=[]
        plt.gca().set_color_cycle('None')
        if not self.chosen_labels:
            print "Your list is empty"
        self.clear_axes()  
        clear()

        for lbl in self.chosen_labels:
            lab_tab = self.data[np.where(np.floor(self.data[:,1])==int(lbl))]
            if  self.species_tab.shape[0]==0:
                self.species_tab = lab_tab
            else:
                self.species_tab=np.append(self.species_tab,lab_tab,axis=0)
        self.make_plot()
        
        plt.draw()
        self.cid = fig.canvas.mpl_connect('button_press_event', 
                                           self.click_on_plot)
           

    def click_on_plot(self,event):
        #Print x,y coords if user clicks on plot
        xcoord,ycoord=[event.xdata,event.ydata]
        r_ind= np.abs(ycoord-self.species_tab[:,6]).argmin()
        self.species_tab = np.delete(self.species_tab,r_ind,0)
        for i in [0,1,2]:
            ax[i].set_color_cycle('None')
        self.clear_axes()
        self.make_plot()
        print "Switch [m]odel, change [v]t, [q]uit or any other key to plot"
    
    def switch_model(self,org_pars):
        old_model= org_pars['model_in']
        print "Name of file with new model of atmosphere?"
        new_model = raw_input()
        org_pars['model_in']=["\'"+new_model+"\'"]
        try:
            run_moog(driver,org_pars)
        except:
            print "\n No such a file"
            org_pars['model_in']=[old_model]
            time.sleep(1.5)
            
    def change_vt(self,org_pars,vt):
        #Edit model
        model=open(org_pars['model_in'][0][1:-1]).readlines()
        vt_ind = 4+int(re.search(r'\d+', model[2]).group())
        model[vt_ind]= "%9.2fE+05\n" % float(vt)
        #Write modified model to temporary file
        mout=open('temp.mod','w')
        for item in model:
            mout.write(item)
        mout.close()
        org_pars['model_in']=['\'temp.mod\'']
        run_moog(driver,org_pars)
           
    def run(self):
        plot_again=''
        self.data=out2_ab(org_pars['summary_out'][0][1:-1])
        while plot_again!='q':
            self.chosen_labels = self.choose_labels()
            self.update_plot()            
            plt.show()
            print "Switch [m]odel, change [v]t, [q]uit or any other key to plot again"
            plot_again=raw_input()
            if plot_again == 'm':
                self.switch_model(org_pars)
                self.data=out2_ab(org_pars['summary_out'][0][1:-1])
            elif plot_again == 'v':
                print "What is the new microturbulence (km/s)?"
                vt=raw_input()
                
                self.change_vt(org_pars,vt)
                self.data=out2_ab(org_pars['summary_out'][0][1:-1])

            self.species_tab=np.array([])
            clear()
         
###############################################################
#It all starts here
clear = lambda: os.system('clear')
clear()
syn_file=sys.argv[1]
driver,params = list_to_dict(open(syn_file).read())
try:
    run_moog(driver,params)
except:
    print "#####################\n Cannot run MOOG."
    print "Check batch.par file and your input file for errors."
    exit()

params['veil']=0.
params['title']=""
org_pars=copy.deepcopy(params)

SM_style()
plt.ion()
if driver == 'synth' and params['plotpars'][0]==1:
    
    fig=plt.figure(figsize=(15, 10),dpi=70)
    p = SynthPlot(org_pars)
    p.run_synth()
        
elif driver == 'abfind':
    
    fig, ax = plt.subplots(3)
    plt.subplots_adjust(hspace=0.5,right=0.9)

    p = ABPlot(org_pars, ax)
    p.run()

elif driver == 'ewfind':
    print_driver(driver)
    run_moog(driver,params)
    
