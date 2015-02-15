# MultiFit
Software for multipeak fitting Raman Spectra of Carbon Materials

Usage 
======
(note the corerct use of flags): 

For single file: 
python multifit.py -f filename n

For batch fitting:
python multifit.py -b n

where n:

0: PseudoVoigt
1: Gaussian
2: Lorentzian

Fitting parameters are initialized within the
"input_parameters.xlsx" Excel file.

Installation
=============

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

Support is know planned any time soon. It is recommended to install the following libraries:
    
    lmfit
    scipy
    matplotlib
    openpyxl