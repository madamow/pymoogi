# README #

This python wrapper for MOOG allows you to use *ewfind* (non-interactive), *synth* and *abfind* drivers in an interactive way without the need for SuperMongo package. I kept the original MOOG layout, and added some minor improvements. You will find all MOOG source files in this repository (MOOG version from July 2014). All your MOOG's configuration files should work with this wrapper. For *synth* driver observed spectrum must be in text format (at least for now). To learn more about MOOG, visit Chris Sneden's webpage: [MOOG](http://www.as.utexas.edu/~chris/moog.html)

 
### How do I get set up? ###
All MOOG source files are in this repository and will be downloaded automatically. If you have some MOOG version already installed, do not worry - those versions will not interact in any way.

The pyMOOGi was tested on Mac OS X and Linux machines. If you are a Windows user, sorry but you are on your own. 

To use pyMOOGi you need [gfortran](https://gcc.gnu.org/wiki/GFortranBinaries) to compile  MOOG's sources and basic python libraries. If you are already familiar with python, you probably have them already installed.

For those who have never worked with python before:
It is not necessary for you to know python to use pyMOOGi. You just need to have it working. 
If you have computer with Mac OS X or Linux, python is already there. It may be outdated, you will probably need to install libraries, but it is there.
For easy updates and installing libraries I strongly recommend [miniConda](http://conda.pydata.org/miniconda.html). Just follow the instructions and make sure that your .bashrc file or .profile file is properly configured.

For running pyMOOGi you will need:

 * python 2.7
 * numpy (I use version 1.10.2)
 * scipy (I use version 0.16.1)
 * matplotlib (I use version 1.5.1)
 * make sure you can use matplotlib backend called 'qt5Agg' (if you decided to install python and its libraries with miniConda, this backend was installed automatically with matplotlib)

### I have python set, what now? ###

* clone or download pyMOOGi from repository
* export path to moog directory:

  `export MOOGPATH=/your/path/to/pymoogi/pymoogi/moog`

Make sure that your system noticed those changes: check your .bashrc or .profile file, you should see MOOGPATH there. 
Do not forget to `source` your .bashrc or .profile file.

* go to /your/path/to/pymoogi/pymoogi/moog
* run Makefile (just type `make` in terminal) - there might be some warnings, but at the end you should get an executable file called MOOG
* go to /your/path/to/pymoogi/pymoogi/moog and run setup file:
`python setup.py install`
* now you are ready to run some calculations. Go to example catalog and type:

`pymoogi synth_example.par`


#### Who do I talk to? ####

* Email me if you need any help or if you have an idea how to make pymoogi better:
madamow[at]icloud.com
