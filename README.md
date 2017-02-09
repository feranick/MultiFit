# MultiFit
Software for multipeak fitting Raman Spectra of Carbon Materials

Reference: N. Ferralis et al. Carbon 108 (2016), 440-449.

Note
=====

This software currently supports only these exitation energies:
- 633 nm

More will be supported in the future.

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

where n:
    0: PseudoVoigt
    1: Gaussian
    2: Lorentzian
    3. Voigt


6. FFT filtering background subtraction
./multifit.py -c filename cutoff

7. Create new input paramter file (csv)
./multifit.py -i

Fitting parameters are initialized within the
"input_parameters.csv" Excel file.

8. Unattended runtime (runs in the background in a headless workstation)

    multifit.py -m filename.txt 0 &>> log.txt &

    or:
    
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

Multifit should work on Windows with the proper dependencies installed (see above).
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

v.5: Added functionality: background subtraction via high bandpass FFT filtering for
correcting high florescence spectra.

v.4: Move back to the original input file format for better compatibility. An input file
with the same capabilities of v.3 can be created using new flag. New advanced analysis.

v.3: New peak added in init file at 1050 1/cm. This makes it incompatible 
with previous version

v.2: It uses a peak guessing algorithm, for more accurate results. The initial peak
is at 1140 1/cm

v.1: It uses a static initialization for the fitting parameters

Known Issues
============

lmfit version 0.9 and 0.9.2 introduced a bug where parameters for PseudoVoigt fits are 
missing, generating an error in MultiFit as a result. The bug has been fixed in version 9.3 
for lmfit. If your distribution has not yet been updated, you can update it manually using 
pip:

	sudo pip install --upgrade lmfit
