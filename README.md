# MultiFit
Software for multipeak fitting Raman Spectra of Carbon Materials

Usage 
======
(note the correct use of flags): 

1. For single file: 
./multifit.py -f filename n

2. For batch fitting:
./multifit.py -b n

3. For map fitting (map acquired with Horiba LabSpec5):
./multifit.py -m filename n

4. Create and save plot data only (no fitting):
./multifit.py -p filename

5. Create and save plot batch data (no fitting):
./multifit.py -p

6. Create new input paramter file (csv)
./multifit.py -i

where n:

0: PseudoVoigt
1: Gaussian
2: Lorentzian
3. Voigt

Fitting parameters are initialized within the
"input_parameters.csv" Excel file.


3. For Headless workstations:
uncomment the two lines in multifit.py:
    import matplotlib
    matplotlib.use('Agg')

4. unattended runtime (runs in the background in a headless workstation)

    nohop multifit.py > -m filename n > log.txt

Log.txt will contain the output generated during the fit and usually displayed in the terminal.

Installation
=============

The following dependencies are required:

    lmfit
    scipy (>0.11)
    matplotlib

These can be installed through the system repository (apt, macports, etc) or by 
python's:

    sudo easy_install lmfit 

1. Ubuntu/Debian:
-----------------

Install dependencies:

    sudo apt-get install python-matplotlib python-scipy
    sudo easy_install lmfit

2. OS X:
---------

Install Macports from http://macports.org
Update ports:

    sudo port selfupdate
    sudo port upgrade outdated.

Install the following ports:

    sudo port install py-lmfit py-scipy py-matplotlib

3. MS Windows:
---------------

Multifit should work on Windows with the proper dependencies installed.
Support is not available.

========================================================================

Fitting Raman maps (mapfit)
========================================================================

The current version can open Raman maps (Horiba LabSpec5, saved as text files)
and fits each spectra in the map. While it does not yet produce a visual 
map of the results, these are saved as (x, y, D5G). Plotting maps from
the computed results is possible through a R script "plotramap.R"
saved in /plotrmap. You can run the script with R. Make sure the filename is
correctly set as the inputFile variable in the R script.


Future releases will allow for more flexibility as well as integrated plotting.

=========================================================================

Version history:
================

v.2: It uses a peak guessing algorithm, for more accurate results.  

v.1: It uses a static initialization for the fitting parameters

