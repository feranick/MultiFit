# MultiFit
Software for multipeak fitting Raman Spectra of Carbon Materials

Usage 
======
(note the corerct use of flags): 

1. For single file: 
python multifit.py -f filename n

2. For batch fitting:
python multifit.py -b n

3. For map fitting (map acquired with Horiba LabSpec5):
python multifit.py -m filename n

4. Create new input paramter file (xlsx)
python multifit.py -i

where n:

0: PseudoVoigt
1: Gaussian
2: Lorentzian

Fitting parameters are initialized within the
"input_parameters.xlsx" Excel file.


3. For Headless workstations:
uncomment the two lines in multifit.py:
    import matplotlib
    matplotlib.use('Agg')

Installation
=============

The following dependencies are required:

    lmfit
    scipy
    matplotlib
    openpyxl (> 2.1.4)

These can be installed through the system repository (apt, macports, etc) or by 
python's:

    sudo easy_install lmfit 

1. Ubuntu/Debian:
-----------------

Install dependencies:

    sudo apt-get install python-matplotlib python-scipy python-openpyxl
    sudo easy_install lmfit

2. OS X:
---------

Install Macports from http://macports.org
Update ports:

    sudo port selfupdate
    sudo port upgrade outdated.

Install the following ports:

    sudo port install py-lmfit py-scipy py-matplotlib py-openpyxl

3. MS Windows:
---------------

Multifit should work on Windows with the proper dependencies installed.
Support is not available.

========================================================================

Experimental support for fitting Raman maps (mapfit)
====================================================

The current version has a class that opens the Raman map (Horiba LabSpec5, 
saved in text file), and fits each spectra in the map. It does not produce (yet) 
a visual map of the results, which are saved as (x, y, D5G). Future releases
will allow for more flexibility as well as plotting.
