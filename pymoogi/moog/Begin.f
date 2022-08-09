
      subroutine begin
c***************************************************************************
c     This routine simply starts up MOOG
c     THIS VERSION IS FOR LINUX REDHAT MACHINES
c***************************************************************************

      implicit real*8 (a-h,o-z)
      include 'Atmos.com'
      include 'Pstuff.com'
      character*80 line, systemcall
      integer num


c*****open data files carried with the source code: Barklem damping
      nfbarklem = 35
      num = 60
      call getcount (num,moogpath)
      if (moogpath(num:num) .ne. '/') then
         num = num + 1
         moogpath(num:num) = '/'
      endif
      fbarklem(1:num) = moogpath(1:num)
      fbarklem(num+1:num+11) = 'Barklem.dat'
      open (nfbarklem,file=fbarklem)


c*****open data files carried with the source code: Barklem UV damping
      nfbarklemUV = 36
      num = 60
      call getcount (num,moogpath)
      if (moogpath(num:num) .ne. '/') then
         num = num + 1
         moogpath(num:num) = '/'
      endif
      fbarklemUV(1:num) = moogpath(1:num)
      fbarklemUV(num+1:num+13) = 'BarklemUV.dat'
      open (nfbarklemUV,file=fbarklemUV)
 

c  write a header and find the appropriate parameter file, and exit normally
      write (array,1001)
      istat = ivwrite (1,1,array,79)
      write (array,1004)
      istat = ivwrite (2,1,array,79)
      array = 'MOOG PARAMETERS? ' 
      nchars = 15
      nfparam = 50     
      lscreen = 4
      if (silent .eq. 'y') then
         fparam = 'batch.par'
      else
         fparam = 'no_filename_given'     
      endif
      call infile ('input  ',nfparam,'formatted  ',0,nchars,
     .             fparam,lscreen)
      read (nfparam,1002) control
      write (array,1003) control
      istat = ivwrite (2,1,array,58)
      write (array,1001)
      istat = ivwrite (3,1,array,79)
      return


c*****format statements
1001  format (79('*'))
1002  format (a7)
1003  format (22x,'MOOG IS CONTROLLED BY DRIVER ',a7)
1004  format (25(' '),'MOOG LTE VERSION (FEB 2017)',26(' '))   
1010  format (a80)
1011  format (i3)


      end
      







