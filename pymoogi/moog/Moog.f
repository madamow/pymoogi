
      program moog
c******************************************************************************
c     This is the main driver for MOOG.  It reads the parameter
c     file and sends MOOG to various controlling subroutines.
c     This is the normal interactive version of the code; for batch
c     processing without user decisions, run MOOGSILENT instead.
c******************************************************************************

      include 'Atmos.com'
      include 'Pstuff.com'
      character yesno*1


c$$$$$$$$$$$$$$$$$$$$$$$$ USER SETUP AREA $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
c*****in compiling MOOG, here the various machine-specific things are 
c     declared.  First, define the directory where MOOG lives, in order to 
c     be able to pull in auxiliary data files; executing 'make' will 
c     generate a reminder of this necessity
c      write (moogpath,1001)
c      moogpath =
c     .  '/Users/myszka/Documents/Nauka/moog'
      call getenv("MOOGPATH", moogpath)

c*****What kind of machine are you using?  Possible ones are:
c     "mac" = Intel-based Apple Mac 
c     "pcl" = a PC or desktop running some standard linux like Redhat
c     "uni" = a machine running Unix, specifically Sun Solaris
      machine = "mac"


c*****declare this to be the normal interactive version; variable "silent"
c     will be queried on all occasions that might call for user input;
c     DON'T CHANGE THIS VARIABLE; 
c     if silent = 'n', the normal interactive MOOG is run;
c     if silent = 'y', the non-interactive MOOG is run
      silent = 'y'
      
c*****invoke the overall starting routine
1     control = '       '
      call begin


c*****use one of the standard driver routines ("isotop" is obsolete):
      if     (control .eq. 'synth  ') then
         call synth  
      elseif (control .eq. 'abfind ') then
         call abfind
      elseif (control .eq. 'ewfind ') then
         call ewfind
      elseif (control .eq. 'blends ') then
         call blends

c*****or, put in your own drivers in the form below....
      elseif (control .eq. 'mine  ') then
         call  mydriver 


c*****or else you are out of luck!
      else
         array = 'THIS IS NOT ONE OF THE DRIVERS.  TRY AGAIN (y/n)?'
         istat = ivwrite (4,3,array,49)
         istat = ivmove (3,1)
         read (*,*) yesno
         if (yesno .eq. 'y') then
            go to 1
         else
            call finish (0)
         endif
      endif


c*****format statements
1001  format (60(' '))
1002  format ('The "isotop" driver is obsolete; "synth" does ',
     .        'its functions now!')
1003  format (22x,'MOOG IS CONTROLLED BY DRIVER ',a7)
1017  format ('x11 -bg black -title MOOGplot -geom 700x800+650+000')
1018  format ('x11 -bg black -title MOOGplot -geom 1200x350+20+450')


      end

      
