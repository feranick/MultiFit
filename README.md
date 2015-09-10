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

Multifit.py is compatible with both Python 2.6-2.7 and Python 3.x. Since the requied dependencies support both Python 2.x and 3.x, you should be able to use either.

The following dependencies are required:

    lmfit
    scipy (>0.11)
    numpy

These can be installed through the system repository (apt, macports, etc) or by python's:

    sudo easy_install lmfit 
or 
    sudo pip install lmfit


1. Ubuntu:
-----------------

Multifit runs on any recent version of Ubuntu. This has been tested with versions as early as Trusty (14.04).
Install dependencies:

    sudo apt-get install python-matplotlib python-scipy
    sudo easy_install lmfit


2. Debian 7 (Wheezy) and Raspbian (for Raspberry PI)
-----------------------------------------------------

Multifit runs with a little work on Debian 7 and Raspbian. Start by installing python-pip and other required programs:

    sudo apt-get install python-pip gfortran python-dev liblapack*

Then you can use pip to install the updated dependencies:

    sudo pip install numpy --update
    sudo pip install scipy --update
    sudo pip install lmfit --update

This might take a while. 

3. OS X:
---------

Install Macports from http://macports.org
Update ports:

    sudo port selfupdate
    sudo port upgrade outdated.

Install the following ports:

    sudo port install py-lmfit py-scipy py-matplotlib

4. MS Windows:
---------------

Multifit should work on Windows with the proper dependencies installed see above).
Support is not available.

========================================================================

Fitting Raman maps
========================================================================

MultiFit.py can open Raman maps saved from Horiba LabSpec5 as text files,
and it can fit each spectra in the map. While it does not yet produce a visual 
map of the results, these are saved as (x, y, D5G). Plotting maps from
the computed results is possible through a R script "plotramap.R"
saved in /plotrmap. You can run the script with R. Make sure the filename is
correctly set as the inputFile variable in the R script.

Important note: The first two entries in the map file from Labspec are empty. 
For MultiFit.py to work, please add 1 to the first two entries. For example, 
for the first line of the file looking like:

		1000.4694	1001.6013	1002.7333

Change it to:

1	1	1000.4694	1001.6013	1002.7333

This is a known issue.

=========================================================================

Version history:
================

v.2: It uses a peak guessing algorithm, for more accurate results.  

v.1: It uses a static initialization for the fitting parameters

