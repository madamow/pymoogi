#     makefile for MOOG with all of the common block assignments;
#     this is for my Mac laptop

#     here are the object files
OBJECTS = Abfind.o Batom.o Begin.o  \
	Blankstring.o Blends.o Bmolec.o Boxit.o \
	Cdcalc.o Chabund.o  \
	Correl.o Crosscorr.o Curve.o Damping.o Discov.o \
	Eqlib.o Estim.o Ewfind.o \
	Ewweighted.o Fakeline.o Finish.o \
	Gammabark.o Getasci.o Getcount.o Getnum.o Getsyns.o \
	Infile.o Inlines.o Inmodel.o Invert.o \
	Jexpint.o Lineinfo.o Lineabund.o Linlimit.o \
	Minimax.o Molquery.o Moog.o Mydriver.o \
	Nansi.o Nearly.o Number.o Obshead.o \
	Oneline.o Opaccouls.o OpacHelium.o OpacHydrogen.o \
	Opacit.o Opacmetals.o Opacscat.o Params.o Partfn.o \
	Partnew.o Plotremember.o  \
	Prinfo.o Putasci.o Readobs.o \
	Rinteg.o Setmols.o Smooth.o Stats.o Sunder.o Synspec.o \
	Synth.o Tablepop.o Taukap.o Total.o Trudamp.o Ucalc.o Vargauss.o \
	Vmacro.o Voigt.o \
        Weedout.o Wavecalc.o Writenumber.o


#     here are the common files
COMMON =  Atmos.com Dummy.com Equivs.com Factor.com Kappa.com Linex.com \
	Mol.com Multistar.com Obspars.com Plotval.com Pstuff.com \
	Quants.com Multimod.com Dampdat.com

#edit this file here if you prefer other compiler
CC = cc
FC = gfortran
FFLAGS = -O2 -g


#        here are the compilation and linking commands
all: MOOG ;
	@echo -----------------------------------------------------------------
	@echo 
	@echo Compilation successful.
	@echo Now export the MOOG_PATH.
	@echo check README.md file for instructions
	@echo
	@echo NOTE: with this version of MOOG 
	@echo you can use ewfind synth and abfind drivers only
	@echo
	@echo -----------------------------------------------------------------

MOOG:  $(OBJECTS);
	$(FC) $(FFLAGS) $(OBJECTS) -static-libgfortran -o MOOG

$(OBJECTS): $(COMMON)

clean:
	-rm -f *.o MOOG libMOOG.a
