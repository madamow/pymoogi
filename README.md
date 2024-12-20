# README #

This Python wrapper for MOOG allows you to use  ***ewfind***, ***blends*** (non-interactive), ***synth***, and ***abfind*** drivers in an interactive way without the SuperMongo package. I kept the original MOOG layout and added some minor improvements. You will find all MOOG source files in this repository (**MOOG version from November 2019**). All your MOOG's configuration files should work with this wrapper. For *synth* driver observed spectrum must be in text format (at least for now). To learn more about MOOG, visit Chris Sneden's webpage: [MOOG](http://www.as.utexas.edu/~chris/moog.html)

 
### How do I get set up? ###
All MOOG source files are in this repository and will be downloaded automatically. If you have a MOOG version already installed, do not worry - those versions will not interact in any way.

The pyMOOGi was tested on Mac OS X and Linux machines. I'm sorry, but you're on your own if you're a Windows user. 

To use pyMOOGi, you need [gfortran](https://gcc.gnu.org/wiki/GFortranBinaries) to compile MOOG's sources and basic Python libraries. 
You don't need to know Python to use pyMOOGi. 

To get pyMOOGi follow these steps:
* clone or download pyMOOGi from its repository
* export path to moog directory:

  `export MOOGPATH=/your/path/to/pymoogi/pymoogi/moog`

Please make sure your system notices those changes: check your .bashrc or .profile file; you should see MOOGPATH there. 
Do not forget to `source` your .bashrc, .profile, or equivalent file.

* go to /your/path/to/pymoogi/pymoogi/moog
* run Makefile (type `make` in the terminal) - there might be some warnings, but at the end, you should get an executable file called MOOG
* go to /your/path/to/pymoogi/ and run the Python setup:
  `pip install .`
  During the setup, all missing Python libraries will be installed if needed.
* now you are ready to run some calculations. Go to the example catalog and type:

`pymoogi synth_example.par`

### Issues

The most common issue with running pyMOOGi is getting the MOOG executable, especially for Mac OS X users.
Please note that I may not be able to help you with solving issues that are specific to your machine that stop you from getting a MOOG executable
(like missing libraries, non-standard OS configurations, multiple versions of Python, etc.).
.

My general tip for Mac OS X users is to make sure that their XCode is up to date. Having XCode Tools installed may also help.

For issues related to pyMOOGi - report an issue. Please use the **Issues** tab at the top of the pyMOOGi GitHub page, and then start **New issue**.

#### Who do I talk to? ####

* Email me if you have an idea how to make pymoogi better:
madamow[at]icloud.com
