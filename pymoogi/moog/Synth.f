
      subroutine synth                   
c******************************************************************************
c     This program synthesizes a section of spectrum and compares it
c     to an observation file.
c******************************************************************************

      implicit real*8 (a-h,o-z)
      include 'Atmos.com'
      include 'Factor.com'
      include 'Mol.com'
      include 'Linex.com'
      include 'Pstuff.com'
      include 'Dummy.com'


c*****examine the parameter file
      call params


c*****open the files for: standard output, raw spectrum depths, smoothed 
c     spectra, and (if desired) IRAF-style smoothed spectra
      nf1out = 20     
      lscreen = 4
      array = 'STANDARD OUTPUT'
      nchars = 15
      call infile ('output ',nf1out,'formatted  ',0,nchars,
     .             f1out,lscreen)
      nf2out = 21               
      lscreen = lscreen + 2
      array = 'RAW SYNTHESIS OUTPUT'
      nchars = 20
      call infile ('output ',nf2out,'formatted  ',0,nchars,
     .             f2out,lscreen)
      if (plotopt .ne. 0) then
         nf3out = 22               
         lscreen = lscreen + 2
         array = 'SMOOTHED SYNTHESES OUTPUT'
         nchars = 25
         call infile ('output ',nf3out,'formatted  ',0,nchars,
     .                f3out,lscreen)
         if (f5out .ne. 'optional_output_file') then
            nf5out = 26
            lscreen = lscreen + 2
            array = 'POSTSCRIPT PLOT OUTPUT'
            nchars = 22
            call infile ('output ',nf5out,'formatted  ',0,nchars,
     .                   f5out,lscreen)
         endif
      endif
      if (iraf .ne. 0) then
         nf4out = 23               
         lscreen = lscreen + 2
         array = 'IRAF ("rtext") OUTPUT'
         nchars = 24
         call infile ('output ',nf4out,'formatted  ',0,nchars,
     .                f4out,lscreen)
      endif

c*****open and read the model atmosphere file
      nfmodel = 30
      lscreen = lscreen + 2
      array = 'THE MODEL ATMOSPHERE'
      nchars = 20
      call infile ('input  ',nfmodel,'formatted  ',0,nchars,
     .             fmodel,lscreen)
      call inmodel

c*****open the line list file and the strong line list file
      nflines = 31
      lscreen = lscreen + 2
      array = 'THE LINE LIST'
      nchars = 13
      call infile ('input  ',nflines,'formatted  ',0,nchars,
     .              flines,lscreen)
      if (dostrong .gt. 0) then
         nfslines = 32
         lscreen = lscreen + 2
         array = 'THE STRONG LINE LIST'
         nchars = 20
         call infile ('input  ',nfslines,'formatted  ',0,nchars,
     .                 fslines,lscreen)
      endif
      
c*****do the syntheses
      choice = '1'
      ncall = 1
      call getsyns (lscreen,ncall)
      call smooth (-1,ncall)   
      call finish (0)
      end 





