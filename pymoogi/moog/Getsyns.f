
      subroutine getsyns (lscreen,ncall)
c******************************************************************************
c     This routine commands the syntheses to be done (or resyntheses if 
c     abundances or isotopic ratios are changed)
c******************************************************************************

      implicit real*8 (a-h,o-z)
      include 'Atmos.com'
      include 'Linex.com'
      include 'Pstuff.com'
      include 'Factor.com'
      include 'Dummy.com'


c*****now do the syntheses
      if (numpecatom .eq. 0 .or. numatomsyn .eq. 0) then
         isynth = 1
         isorun = 1
         nlines = 0
         mode = 3
         call inlines (1)
         call eqlib
         call nearly (1)
         call synspec
      else
         do n=1,numatomsyn
            isynth = n
            isorun = n
            start = oldstart
            sstop = oldstop
            mode = 3
            molopt = 2
            call inlines (1)
            call eqlib
            call nearly (1)
            call synspec
            linprintopt = 0
         enddo
      endif
      return
         

c*****a nonsense situation:  the line list read in successfully at the
c*****start, but now there is a problem on re-synthesis
10    write (*,1108)
      stop


c*****format statements
1002  format (13('-'),'MOOG OUTPUT FILE',10('-'),
     .        '(MOOG version from 23/04/07)',13('-')//
     .        'THE MODEL TYPE: ',a10)
1003  format ('   The Rosseland opacities and optical depths have ',
     .        'been read in')
1102  format (/'MODEL ATMOSPHERE HEADER:'/a80/)
1103  format ('INPUT ATMOSPHERE QUANTITIES',10x,
     .        '(reference wavelength =',f10.2,')'/3x,'i',2x,'xref',3x,
     .        'tauref',7x,'T',6x,'logPg',4x,'Pgas',6x,'logPe',
     .        5x,'Ne',9x,'Vturb'/
     .        (i4,0pf6.2,1pd11.4,0pf9.1,f8.3,1pd11.4,0pf8.3,
     .        1pd11.4,d11.2))
1104  format (/'INPUT ABUNDANCES: (log10 number densities, log H=12)'/
     .       '      Default solar abundances: Asplund et al. 2009')
1105  format (5(3x,a2,'(',i2,')=',f5.2))
1106  format (/'OPTIONS: atmosphere = ',i1,5x,'molecules  = ',i1/
     .        '         lines      = ',i1,5x,'flux/int   = ',i1)
1107  format (/'KAPREF ARRAY:'/(6(1pd12.4)))
1108  format ('something odd: linelist was OK initially, now cannot ',
     .        'be read; I QUIT!')


      end 





