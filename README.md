# README #

This python wrapper for MOOG allows you to use  ***ewfind***, ***blends*** (both non-interactive), ***synth***  and ***abfind*** drivers in an interactive way without the need for SuperMongo package. I kept the original MOOG layout, and added some minor improvements. You will find all MOOG source files in this repository (**MOOG version from November 2019**). All your MOOG's configuration files should work with this wrapper. For *synth* driver observed spectrum must be in text format (at least for now). To learn more about MOOG, visit Chris Sneden's webpage: [MOOG](http://www.as.utexas.edu/~chris/moog.html)

 
### How do I get set up? ###
All MOOG source files are in this repository and will be downloaded automatically. If you have some MOOG version already installed, do not worry - those versions will not interact in any way.

The pyMOOGi was tested on Mac OS X and Linux machines. If you are a Windows user, sorry but you are on your own. 

To use pyMOOGi you need [gfortran](https://gcc.gnu.org/wiki/GFortranBinaries) to compile  MOOG's sources and basic python libraries. If you are already familiar with python, you probably have them already installed.

For those who have never worked with python before:
It is not necessary for you to know python to use pyMOOGi. You just need to have it working. 
If you have computer with Mac OS X or Linux, python is already there. It may be outdated, you will probably need to install libraries, but it is there.
For easy updates and installing libraries I strongly recommend [miniConda](http://conda.pydata.org/miniconda.html). Just follow the instructions and make sure that your .bashrc file or .profile file is properly configured.

For running pyMOOGi you will need:

 * python3
 * numpy 
 * scipy 
 * matplotlib 
 * make sure you can use matplotlib backend called 'qt5Agg' (if you decided to install python and its libraries with miniConda, this backend was installed automatically with matplotlib)

### I have python set, what now? ###

* clone or download pyMOOGi from repository
* export path to moog directory:

  `export MOOGPATH=/your/path/to/pymoogi/pymoogi/moog`

Make sure that your system noticed those changes: check your .bashrc or .profile file, you should see MOOGPATH there. 
Do not forget to `source` your .bashrc, .profile, or eqiuvalent file.

* go to /your/path/to/pymoogi/pymoogi/moog
* run Makefile (just type `make` in terminal) - there might be some warnings, but at the end you should get an executable file called MOOG
* go to /your/path/to/pymoogi/ and run setup file:

`python setup.py install`

If you have more than one Python distribution and are unsure which one is the default one, run

`python3 setup.py install`

instead. This will point pyMOOGi to python3. 

* now you are ready to run some calculations. Go to example catalog and type:

`pymoogi synth_example.par`

### Issues

The most common issue with running pyMOOGi seems to be getting MOOG executable, especially for Mac OS X users.
Please mind that I may not be able to help you with solving issues that are specific to your machine
(like missing libraries, non-standard OS configurations, multiple versions of python etc.)
that stop you from getting a MOOG executable.

My general tip for Mac OS X users: make sure that your XCode is up to date, having XCode Tools installed may also help.

For issues related to pyMOOGi - report an issue. Please use **Issues** tab at the top of pyMOOGi github page, and then start **New issue**.

#### Who do I talk to? ####

* Email me if you have an idea how to make pymoogi better:
madamow[at]icloud.com
