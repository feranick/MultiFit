# MultiFit
Software for multipeak fitting Raman Spectra of Carbon Materials

Usage (note the corerct use of flags): 

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
