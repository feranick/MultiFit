#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
=============================================================
 Multifit 5 (version: 5-20170109b)
 
 (2015-2017) Nicola Ferralis <feranick@hotmail.com>
 
 The entire code is covered by GNU Public License (GPL) v.3
=============================================================
'''
print(__doc__)

import matplotlib
if matplotlib.get_backend() == 'TkAgg':
    matplotlib.use('Agg')

from numpy import *
from lmfit.models import GaussianModel, LorentzianModel, PseudoVoigtModel, VoigtModel
import matplotlib.pyplot as plt
import sys, os.path, getopt, glob, csv
from os.path import exists
from os import rename
from multiprocessing import Pool
import multiprocessing as mp
from datetime import datetime, date

####################################################################
''' Program definitions and configuration variables '''
####################################################################
class defPar:
    ### init file
    typeInitFile = 0  #(0: LM; 1: HM)
    
    ### Define number of total peaks (do not change: this is read from file)
    numPeaks = 0
    ### Name input paramter file
    inputParFile = 'input_parameters.csv'
    # Save summary fitting results
    summary = 'summary.csv'
    # max reduced chi square for reliable results
    redchi = 10
    # value assigned to D5G wheen fit is wrong
    outliar = 0
    ### Plot initial fitting curve
    initCurve = True
    ### Multiprocessing?
    multiproc = True
    ### Max number of processor. Uncomment:
    ###     first: max allowed by hardware
    ###     second: max specified.
    numProc = mp.cpu_count()
    #numProc = 4
    
    ### Peak search optimization
    peakPosOpt = False
    
    ### Resolution for plots
    dpiPlot = 150
    formatPlot = 0  #png
    #formatPlot = 1  #svg
    custAspRatio = False
    xAspRatio = 10
    yAspRatio = 3
    padAspRatio = 1.3
    
    ### Parameters for H:C conversion - 2016-01-16
    ### Excitation energy: 633 nm
    mHC = 0.871
    bHC = -0.0508
    m2HC = 0.6024
    b2HC = -0.0739
    m3HC = 0.5657
    b3HC = 1.5036

    ### dDeltaOrg correction
    ### Based on Des Marais, Org. GeoChem. (1997) 27:185-193
    dDeltaOrg = True  # Enable for Delta delta org
    dDeltaOrgType = 1  # (1: D5G; 2: D4D5G)
    
    dD1 = 4.2
    dD2 = -11.9
    dD3 = 11.1
    dD4 = -3.4

    ### Initial FFT cutoff for high bandpass filter
    ### Mosier-Boss et al. Applied Spectroscopy (1995) 49:630
    FFTcutoff = 0.005

####################################################################
''' Main routine to perform and plot the fit '''
####################################################################

def calculate(x, y, x1, y1, file, type, processMap, showPlot, lab):
    
    ### Load initialization parameters from csv file.
    with open(defPar.inputParFile, 'rU') as inputFile:
        input = csv.reader(inputFile)
        numRows = 0
        inval=[]
        for row in input:
            defPar.numPeaks = len(row)-1
            row = [nulStrConvDigit(entry) for entry in row]
            inval.append(row)
            numRows +=1
        inputFile.close()
    inv = resize(inval, [numRows, defPar.numPeaks+1])
    fpeak = []

    # define active peaks
    for i in range(1, defPar.numPeaks+1):
        fpeak.extend([int(inv[1,i])])

    p = Peak(type)

    numActivePeaks = 0
    for i in range (0, defPar.numPeaks):
        if fpeak[i] != 0:
            numActivePeaks +=1
    print (' Fitting with ' + str(numActivePeaks) + ' (' + p.typec + ') peaks')
    if(defPar.peakPosOpt==True):
        print(' Peak Search Optimization: ON\n')
    else:
        print(' Peak Search Optimization: OFF\n')

    ### Initialize parameters for fit.
    pars = p.peak[0].make_params()
    for i in range (0, defPar.numPeaks):
        if fpeak[i]!=0:

            fac1 = 2
            if (defPar.peakPosOpt == True):
                fac = fac1 - abs(y[ix(x,inv[2,i+1]+fac1*inv[5,i+1])] - y[ix(x,inv[2,i+1]-fac1*inv[5,i+1])]) / \
                    max(y[ix(x,inv[2,i+1]-fac1*inv[5,i+1]):ix(x,inv[2,i+1]+fac1*inv[5,i+1])])
            else:
                fac = fac1
            print(' Peak {:}'.format(str(i)) +': [' + str(inv[2,i+1]-fac*inv[5,i+1]) + ', ' + \
                  str(inv[2,i+1]+fac*inv[5,i+1]) + ']')

            pars += p.peak[i].guess(y[ix(x,inv[2,i+1]-fac*inv[5,i+1]):ix(x,inv[2,i+1]+fac*inv[5,i+1])] , \
                    x=x[ix(x,inv[2,i+1]-fac*inv[5,i+1]):ix(x,inv[2,i+1]+fac*inv[5,i+1])])
            
            pars['p{:}_center'.format(str(i))].set(min = inv[3,i+1], max = inv[4,i+1])
            pars['p{:}_sigma'.format(str(i))].set(min = inv[6,i+1], max = inv [7,i+1])
            pars['p{:}_amplitude'.format(str(i))].set(min=inv[9,i+1], max = inv[10,i+1])
            if (type ==0):
                pars['p{:}_fraction'.format(str(i))].set(min = inv[12,i+1], max = inv[13,i+1])
            if (type ==3):
                pars['p{:}_gamma'.format(str(i))].set(inv[5,i+1])


    ### Add relevant peak to fitting procedure.
    mod = p.peak[1]
    for i in range (2,defPar.numPeaks):
        if fpeak[i]!=0:
            mod += p.peak[i]
    if fpeak[0] != 0:
        mod += p.peak[0]

    ### Initialize prefitting curves
    init = mod.eval(pars, x=x)

    ### Perform fitting and display report
    print('\n************************************************************')
    print(' Running fit on file: ' + file + ' (' + str(x1) + ', ' + str(y1) + ')')
    out = mod.fit(y, pars,x=x)
    print(' Done! \n')
    print(' Showing results for: ' + file + ' (' + str(x1) + ', ' + str(y1) + ')')
    print(out.fit_report(min_correl=0.25))

    ### Output file names.
    outfile = 'fit_' + file         # Save individual fitting results
    plotfile = os.path.splitext(file)[0] + '_fit'   # Save plot as image

    if os.path.isfile(defPar.summary) == False:
        header = True
    else:
        header = False
        print('\nFit successful: ' + str(out.success))

        d5g = out.best_values['p1_amplitude']/out.best_values['p5_amplitude']
        d4d5g = (out.best_values['p0_amplitude']+out.best_values['p1_amplitude'])/out.best_values['p5_amplitude']
        d1g = out.best_values['p2_amplitude']/out.best_values['p5_amplitude']
        d1d1g = out.best_values['p2_amplitude']/(out.best_values['p2_amplitude']+out.best_values['p5_amplitude'])
        hc = defPar.mHC*d5g + defPar.bHC
        hc2 = defPar.m2HC*d4d5g + defPar.b2HC
        hc3 = defPar.m3HC*pow(d4d5g,defPar.b3HC)
        wG = out.best_values['p5_sigma']*2
        if defPar.dDeltaOrg == True:
            if defPar.dDeltaOrgType == 1:
                r_hc = hc
            if defPar.dDeltaOrgType == 2:
                r_hc = hc2
            dDOrg = defPar.dD1 + defPar.dD2*r_hc + defPar.dD3*(r_hc**2) + defPar.dD4*(r_hc**3)


    if (processMap == False):
        if (fpeak[1] == 1 & fpeak[2] == 1 & fpeak[5] == 1):
            print('Fit type: {:}'.format(p.typec))
            print('Reduced Chi-square: {0:.2f} - Chi-square: {1:.2f}'.format(out.redchi, out.chisqr))
            print('\n H:C = {0:.3f} - D5/G = {1:.3f}'.format(hc, d5g))
            print(' H:C = {0:.3f} - (D4+D5)/G = {1:.3f}\n'.format(hc2, d4d5g))
            #print(' H:C - 2 (D4D5G) = {:.3f}'.format(hc3))

            if defPar.dDeltaOrg == True:
                if defPar.dDeltaOrgType == 1:
                    print(' dDeltaOrg (D5G) = {:f}\n'.format(dDOrg))
                if defPar.dDeltaOrgType == 2:
                    print(' dDeltaOrg (D4D5G) = {:f}\n'.format(dDOrg))

            if type ==0:
                print(' G: {:.1f}% Gaussian'.format(out.best_values['p5_fraction']*100))
            print(' D1/G = {:.3f}\n'.format(d1g))

            ### Uncomment to enable saving results of each fit in a separate file.
            '''
                with open(outfile, "a") as text_file:
                text_file.write('\nD5/G = {:f}'.format(d5g))
                text_file.write('\H:C = {:f}'.format(hc))
                text_file.write('\n(D4+D5)/G = {:f}'.format(d4d5g))
                text_file.write('\nD1/G = {:f}'.format(d1g))
                if type ==0:
                    text_file.write('\nG %Gaussian: {:f}'.format(out.best_values['p5_fraction']))
                text_file.write('\nFit type: {:}'.format(p.typec))
                text_file.write('\nChi-square: {:}'.format(out.chisqr))
                text_file.write('\nReduced Chi-square: {:}\n'.format(out.redchi))
            '''

    ### Write Summary


    summaryFile = [file, \
        d5g, d4d5g, hc, hc2, d1g, d1d1g, \
        out.best_values['p2_amplitude'], \
        out.best_values['p0_amplitude'], \
        out.best_values['p1_amplitude'], \
        out.best_values['p5_amplitude'], \
        out.best_values['p5_sigma']*2, \
        out.best_values['p5_center']]

    if type ==0:
        summaryFile.extend([out.best_values['p1_fraction'], \
                        out.best_values['p2_fraction'], \
                        out.best_values['p2_fraction']])
    else:
        for i in range(0,3):
            summaryFile.extend([type-1])
    summaryFile.extend([out.chisqr, out.redchi, p.typec, out.success, \
                    x1, y1, lab])

    if defPar.dDeltaOrg == True:
        summaryFile.extend([dDOrg])

    with open(defPar.summary, "a") as sum_file:
        csv_out=csv.writer(sum_file)
        csv_out.writerow(summaryFile)
        sum_file.close()
    
    if(processMap == True):
        saveMap(file, out, 'D5G', d5g, x1, y1)
        saveMap(file, out, 'D4D5G', d4d5g, x1, y1)
        saveMap(file, out, 'D1G', d1g, x1, y1)
        saveMap(file, out, 'D1GD1', d1d1g, x1, y1)
        saveMap(file, out, 'HC1', hc, x1, y1)
        saveMap(file, out, 'HC2', hc2, x1, y1)
        saveMap(file, out, 'wG', wG, x1, y1)
        saveMapMulti(file, out, hc, hc2, wG, d5g, d1g, d4d5g, d4d5g+d1g, x1, y1, lab,1)
        saveMapMulti(file, out, hc, hc2, wG, out.best_values['p5_amplitude'], \
                     out.best_values['p2_amplitude'], \
                     out.best_values['p1_amplitude'], \
                     out.best_values['p0_amplitude'], x1, y1, lab, 2)

    else:
        if(showPlot == False):
            plt.switch_backend('Agg')
        
        ### Plot optimal fit and individial components
        if(defPar.custAspRatio == False):
            fig = plt.figure()
        else:
            fig = plt.figure(figsize=(defPar.xAspRatio,defPar.yAspRatio))
        ax = fig.add_subplot(111)
        ax.plot(x, y, label='data')
        if(defPar.custAspRatio == True):
            plt.tight_layout(pad=1.3)

        if(defPar.initCurve == True):
            ax.plot(x, init, 'k--', label='initial')
        
        ax.plot(x, out.best_fit, 'r-', label='fit')
        y0 = p.peak[0].eval(x = x, **out.best_values)
        #ax.plot(x,y0,'g')
        y = [None]*(defPar.numPeaks + 1)
        for i in range (0,defPar.numPeaks):
            if (fpeak[i] ==1):
                y[i] = p.peak[i].eval(x = x, **out.best_values)
                if (i==1 or i==5):
                    ax.plot(x,y[i],'g',linewidth=2.0)
                else:
                    ax.plot(x,y[i],'g')

        ax.text(0.01, 0.82, "Fit type: {0:s}\nH:C (D5/G) = {1:.3f}\nH:C (D4D5/G) = {2:.3f}\nRed. Chi sq: {3:.2f}".format( \
                                p.typec, hc, hc2, out.redchi), transform=ax.transAxes)

        plt.xlabel('Raman shift [1/cm]')
        plt.ylabel('Intensity [arb. units]')
        plt.title(file)
        plt.legend()
        plt.grid(True)
        plt.xlim([min(x), max(x)])

        if(defPar.formatPlot == 0):
            plt.savefig(plotfile + '.png', dpi = defPar.dpiPlot, format = 'png')  # Save plot
        if(defPar.formatPlot == 1):
            plt.savefig(plotfile + '.svg', dpi = defPar.dpiPlot, format = 'svg')  # Save plot

        if(showPlot == True):
            print('*** Close plot to quit ***\n')
            plt.show()
        plt.close()

    del p
    del out

####################################################################
''' Main program '''
####################################################################

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "bfmipch:", ["batch", "file", "bs","type", "map", "input-par", "plot", "help"])
    except getopt.GetoptError:
        # print help information and exit:
        usage()
        sys.exit(2)

    if opts == []:
        usage()
        sys.exit(2)

    # If parameter file not present, make one
    if not exists(defPar.inputParFile):
        print ('\n Input parameter file not found. Generating a new one...')
        genInitPar(defPar.typeInitFile)

    # If summary file is not present, make it and fill header
    makeHeaderSummary()

    if(defPar.multiproc == True):
        print('\n Multiprocessing enabled: ' + str(defPar.numProc) + '/' + str(mp.cpu_count()) + ' CPUs\n')
    else:
        print('\n Multiprocessing disabled\n')
    for o, a in opts:
        if o in ("-b" , "--batch"):
            try:
                type = sys.argv[2]
            except:
                usage()
                sys.exit(2)
            type = int(sys.argv[2])
            i = 0
            if(defPar.multiproc == True):
                p = Pool(defPar.numProc)
                for f in glob.glob('*.txt'):
                    if (f != 'summary.txt'):
                        rs = readSingleSpectra(f)
                        p.apply_async(calculate, args=(rs.x, rs.y, '0', '0', f, type, False, False, i))
                        i += 1
                p.close()
                p.join()
            else:
                for f in glob.glob('*.txt'):
                    if (f != 'summary.txt'):
                        rs = readSingleSpectra(f)
                        calculate(rs.x, rs.y, '0', '0', f, type, False, False, i)
                        i += 1
            addBlankLine(defPar.summary)
        
        elif o in ("-f", "--file"):
            try:
                type = sys.argv[3]
            except:
                usage()
                sys.exit(2)
            file = str(sys.argv[2])
            type = int(sys.argv[3])
            rs = readSingleSpectra(file)
            calculate(rs.x, rs.y, '0', '0', file, type, False, True, '')

        elif o in ("-c", "--bs"):
            try:
                cutoff = str(sys.argv[3])
            except:
                #usage()
                #sys.exit(2)
                print(' Using Suggested FFT cutoff: ' + str(defPar.FFTcutoff) + ')\n')
                cutoff = defPar.FFTcutoff
            file = str(sys.argv[2])
            rs = readSingleSpectra(file)
            bsFFT(rs.x, rs.y, file, float(cutoff), True)

        elif o in ("-p", "--plot"):
            if(len(sys.argv) < 3):
                if(defPar.multiproc == True):
                    p = Pool(defPar.numProc)
                    for f in glob.glob('*.txt'):
                        if (f != 'summary.txt'):
                            rs = readSingleSpectra(f)
                            print ("Saving plot for: " + f)
                            p.apply_async(plotData, args=(rs.x, rs.y, f, False))
                    p.close()
                    p.join()
                else:
                    for f in glob.glob('*.txt'):
                        if (f != 'summary.txt'):
                            rs = readSingleSpectra(f)
                            print ("Saving plot for: " + f)
                            plotData(rs.x, rs.y, f, False)
            else:
                file = str(sys.argv[2])
                rs = readSingleSpectra(file)
                plotData(rs.x, rs.y, file, True)

        elif o in ("-m", "--map"):
            try:
                type = sys.argv[3]
            except:
                usage()
                sys.exit(2)

            file = str(sys.argv[2])
            type = int(sys.argv[3])
            rm = readMap(file)
            map = Map()
            i=0
            if(defPar.multiproc == True):
                p = Pool(defPar.numProc)
                for i in range (1, rm.num_lines):
                    p.apply_async(calculate, args=(rm.x, rm.y[i], rm.x1[i], rm.y1[i], file, type, True, False, i))
                p.close()
                p.join()
            #map.draw(os.path.splitext(file)[0] + '_map.txt', True)

            else:
                for i in range (1, rm.num_lines):
                    calculate(rm.x, rm.y[i], rm.x1[i], rm.y1[i], file, type, True, False, i)
                #map.draw(os.path.splitext(file)[0] + '_map.txt', True)
        
        elif o in ("-i", "--input-par"):
            print (' Generating a new input parameter file...')
            try:
                typeIF = sys.argv[2]
            except:
                typeIF = defPar.typeInitFile
            genInitPar(int(typeIF))

        else:
            usage()
            sys.exit(2)

####################################################################
''' Class to read map files (Horiba LabSpec5) '''
####################################################################

class readMap:
    def __init__(self, file):
        try:
            with open(file) as openfile:
                ### Load data
                self.num_lines = sum(1 for line in openfile)-1
                data = loadtxt(file)
        
                self.x1 = [None]*(self.num_lines)
                self.y1 = [None]*(self.num_lines)
                self.y = [None]*(self.num_lines)
                
                self.x = data[0, 2:]
                for i in range(0, self.num_lines):
                    self.x1[i] = data[i+1, 1]
                    self.y1[i] = data[i+1, 0]
                    self.y[i] = data[i+1, 2:]
        except:
            print(' File: ' + file + ' not found\n')
            sys.exit(2)

####################################################################
''' Class to read individual spectra '''
####################################################################

class readSingleSpectra:
    def __init__(self, file):
        try:
            with open(file):
                data = loadtxt(file)
                self.x = data[:, 0]
                self.y = data[:, 1]
        except:
            print(' File: ' + file + ' not found\n')
            sys.exit(2)

####################################################################
''' Class to define peaks and their properties '''
####################################################################

class Peak:
    ### Define the typology of the peak
    def __init__(self, type):
        
        self.peak= [None]*(defPar.numPeaks)
        
        if type==0:
            for i in range (0,defPar.numPeaks):
                self.peak[i] = PseudoVoigtModel(prefix="p"+ str(i) +"_")
            self.typec = "PseudoVoigt"
        elif type == 1:
            for i in range (0,defPar.numPeaks):
                self.peak[i] = GaussianModel(prefix="p"+ str(i) +"_")
            self.typec = "Gauss"
        elif type == 2:
            for i in range (0,defPar.numPeaks):
                self.peak[i] = LorentzianModel(prefix="p"+ str(i) +"_")
            self.typec = "Lorentz"
        elif type ==3:
            for i in range (0,defPar.numPeaks):
                self.peak[i] = VoigtModel(prefix="p"+ str(i) +"_")
            self.typec = "Voigt"
        else:
            print("Warning: type undefined. Using PseudoVoigt")
            for i in range (0,defPar.numPeaks):
                self.peak[i] = PseudoVoigtModel(prefix="p"+ str(i) +"_")
            self.typec = "PVoigt"

####################################################################
''' Routine to generate initialization parameter file '''
####################################################################

def genInitPar(typeIF):
    newParFile = defPar.inputParFile
    if exists(newParFile):
        rename(newParFile, newParFile.replace(".csv", str(datetime.now().strftime('_%Y-%m-%d_%H-%M-%S.csv'))))
        print(' Input parameter file: ' + defPar.inputParFile + ' already exists. Backing up file.')
               
    if typeIF == 0:
        initPar = [('name', 'D4', 'D5', 'D1', 'D3a', 'D3b', 'G', 'D2', 'Base'), \
                       ('activate peak',1,1,1,1,1,1,1,1), \
                       ('center',1160,1250,1330,1400,1450,1590,1710,1080), \
                       ('center min','',1240,'','','','','',''), \
                       ('center max','',1275,'','','','','',''), \
                       ('sigma',20,20,40,20,10,20,10,20), \
                       ('sigma min',10,10,10,10,5,10,5,10), \
                       ('sigma max',50,50,50,50,50,50,40,50), \
                       ('amplitude','','','','','','','',''), \
                       ('ampl. min',0,0,0,0,0,0,0,0), \
                       ('ampl. max','','','','','','','',''), \
                       ('fraction',0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5), \
                       ('fraction min',0,0,0,0,0,0,0,0), \
                       ('fraction max',1,1,1,1,1,1,1,1)]
            
    if typeIF == 1:
        initPar = [('name', 'D4', 'D5', 'D1', 'D3a', 'D3b', 'G', 'D2'), \
                       ('activate peak',1,1,1,0,1,1,0), \
                       ('center',1160,1250,1330,1400,1470,1590,1680), \
                       ('center min','',1240,'','','','',''), \
                       ('center max','',1275,'','','','',''), \
                       ('sigma',20,20,40,20,10,20,20), \
                       ('sigma min',10,10,10,10,5,10,10), \
                       ('sigma max',50,50,50,50,50,50,50), \
                       ('amplitude','','','','','','',''), \
                       ('ampl. min',0,0,0,0,0,0,0), \
                       ('ampl. max','','','','','','',''), \
                       ('fraction',0.5,0.5,0.5,0.5,0.5,0.5,0.5), \
                       ('fraction min',0,0,0,0,0,0,0), \
                       ('fraction max',1,1,1,1,1,1,1)]
            
    with open(defPar.inputParFile, "a") as inputFile:
        csv_out=csv.writer(inputFile)
        for row in initPar:
            csv_out.writerow(row)
        inputFile.close()

    print(' Input parameter file saved in: ' + defPar.inputParFile + '\n')

####################################################################
''' Make header, if absent, for the summary file '''
####################################################################

def makeHeaderSummary():
    if os.path.isfile(defPar.summary) == False:
        summaryHeader = ['File','D5G','(D4+D5)/G','HC','HC2','D1/G', 'D1/(D1+G)',
            'iD1','iD4','iD5','iG','wG','pG','D5%Gaussian', \
            'D1%Gaussian','G%Gaussianfit','Chi-square',\
            'red-chi-sq','Fit-type','Fit-OK','x1','y1', \
            'label']
        if defPar.dDeltaOrg == True:
            summaryHeader.extend(['dDeltaOrg'])
        with open(defPar.summary, "a") as sum_file:
            csv_out=csv.writer(sum_file)
            csv_out.writerow(summaryHeader)
            sum_file.close()

####################################################################
''' Lists the program usage '''
####################################################################

def usage():
    print(' Website: https://github.com/feranick/MultiFit\n')
    print(' Supported excitation energies: 633 nm\n')
    print('Usage: \n\n - Single file:')
    print(' python multifit.py -f filename n\n')
    print(' - Batch processing:')
    print(' python multifit.py -b n\n')
    print(' - Map (acquired with Horiba LabSpec5): ')
    print(' python multifit.py -m filename n\n')
    print(' - Create and save plot of data only (no fit): ')
    print(' python multifit.py -p filename \n')
    print(' - Create and save plot of batch data (no fit): ')
    print(' python multifit.py -p \n')
    print(' n = 0: PseudoVoigt 1: Gaussian 2: Lorentzian 3: Voigt\n')
    print(' - Create new input parameter file (csv): ')
    print(' python multifit.py -i \n')
    print(' - FFT filtering background subtraction: ')
    print(' python multifit.py -c filename cutoff')
    print(' (suggested cutoff: ' + str(defPar.FFTcutoff) + ')\n')
    
    print(' Important note: The first two entries in the map file from Labspec are empty.')
    print(' For MultiFit.py to work, please add 1 to the first two entries. For example,')
    print(' for the first line of the file looking like:\n')
    print('                 1000.4694	1001.6013	1002.7333...')
    print(' Change it to:\n')
    print(' 1	1	1000.4694	1001.6013	1002.7333...\n\n')

####################################################################
''' Add blank line at the end of the summary spreadsheet '''
####################################################################

def addBlankLine(file):
    try:
        with open(file, "a") as sum_file:
            sum_file.write('\n')
    except:
        print ('File busy!')

####################################################################
''' Finds data index for a given x value '''
####################################################################

def ix(arrval, value):
    #return index of array *at or below* value
    if value < min(arrval): return 0
    return (where(arrval<=value)[0]).max()

####################################################################
''' Convert null or strings into floats '''
####################################################################
                      
def nulStrConvDigit(x):
    if (not x or not x.isdigit()):
        return None
    else:
        return float(x)

####################################################################
''' Drawing only routine '''
####################################################################

def plotData(x, y, file, showPlot):
    ### Plot initial data
    pngData = os.path.splitext(file)[0]   # Save plot as image
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(x, y, label='data')
    plt.xlabel('Raman shift [1/cm]')
    plt.ylabel('Intensity [arb. units]')
    plt.title(file)
    #plt.legend()
    plt.grid(True)

    if(defPar.formatPlot == 0):
        plt.savefig(pngData + '.png', dpi = defPar.dpiPlot, format = 'png')  # Save plot
    if(defPar.formatPlot == 1):
        plt.savefig(pngData + '.svg', dpi = defPar.dpiPlot, format = 'svg')  # Save plot

    if(showPlot == True):
        print('*** Close plot to quit ***\n')
        plt.show()
    plt.close()


####################################################################
''' FFT background correction '''
####################################################################

def bsFFT(x, y, file, cutoff, showPlot):
    
    a1 = cutoff
    ### Plot initial data
    pngData = os.path.splitext(file)[0]   # Save plot as image

    fft_freq = fft.rfftfreq(x.shape[-1])
    fft_y = fft.rfft(y)
    
    lenfreq = len(fft_freq)
    cy = empty_like(fft_y)
    
    ######  HBP filter   ######
    for l in range (0, lenfreq):
        if(l<a1*lenfreq):
            cy.put(l, l/(a1*lenfreq))
        else:
            cy.put(l, 1)
    #########################

    bs_y = fft.irfft(fft_y*cy)
    bs_y = append(bs_y,0)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    #ax.plot(fft_freq, fft_y.real, label='FFT')
    #ax.plot(fft_freq, cy.real, label='cy')
    ax.plot(x, y, label='Initial')
    ax.plot(x, bs_y, label='FFT corrected')
    plt.xlabel('Raman shift [1/cm]')
    plt.ylabel('Intensity [arb. units]')
    plt.title(file)
    plt.legend()
    plt.grid(True)
    
    if(defPar.formatPlot == 0):
        plt.savefig(pngData + '.png', dpi = defPar.dpiPlot, format = 'png')  # Save plot
    if(defPar.formatPlot == 1):
        plt.savefig(pngData + '.svg', dpi = defPar.dpiPlot, format = 'svg')  # Save plot
    
    if(showPlot == True):
        print('*** Close plot to quit ***\n')
        plt.show()
    plt.close()

    outfile = os.path.splitext(file)[0] + '_cutoff-' + str(cutoff) + '_FFTcorr.txt'

    with open(outfile, "a") as text_file:
        for l in range(0, len(x)):
            text_file.write(str(x[l]))
            text_file.write('\t')
            text_file.write(str(bs_y[l]))
            text_file.write('\n')

    print(' FFT corrected spectra saved in: ' + outfile + '\n')



####################################################################
''' Save map files '''
####################################################################

def saveMap(file, out, extension, s, x1, y1):
    inputFile = os.path.splitext(file)[0] + '_' + extension + '_map.csv'
    with open(inputFile, "a") as coord_file:
        coord_file.write('{:},'.format(x1))
        coord_file.write('{:},'.format(y1))
        if (out.success == True and out.redchi < defPar.redchi):
            coord_file.write('{:}\n'.format(s))
        else:
            coord_file.write('{:}\n'.format(defPar.outliar))
        coord_file.close()

def saveMapMulti(file, out, s1, s2, s3, s4, s5, s6, x1, y1, lab, mtype):

    if(mtype == 1):
        inputFile = os.path.splitext(file)[0] + '_map-ratio.csv'
    else:
        inputFile = os.path.splitext(file)[0] + '_map-int.csv'
    
    if (os.path.exists(inputFile) == False):
        with open(inputFile, "a") as coord_file:
            if(mtype == 1):
                coord_file.write(',HC,wG,D5G,D1G,D4D5G,DG,X,Y\n')
            else:
                coord_file.write(',HC,wG,G,D1,D5,D4,X,Y\n')
            coord_file.close()

    with open(inputFile, "a") as coord_file:
        if (out.success == True and out.redchi < defPar.redchi):
            coord_file.write('{:},'.format(lab))
            coord_file.write('{:},'.format(s1))
            coord_file.write('{:},'.format(s2))
            coord_file.write('{:},'.format(s3))
            coord_file.write('{:},'.format(s4))
            coord_file.write('{:},'.format(s5))
            coord_file.write('{:},'.format(s6))
        else:
            coord_file.write('{:},'.format(lab))
            for i in range (0, 6):
                coord_file.write('{:},'.format(defPar.outliar))

        coord_file.write('{:},'.format(x1))
        coord_file.write('{:}\n'.format(y1))
        coord_file.close()

####################################################################
''' Definition of class map'''
####################################################################

class Map:
    def __init__(self):
        self.x = []
        self.y = []
        self.z = []
    
    def readCoord(self, file):
        self.num_lines = sum(1 for line in open(file))
        
        data = genfromtxt(file)
        self.x = data[:,0]
        self.y = data[:,1]
        self.z = data[:,2]
    
    def draw(self, file, showplot):
        self.readCoord(file)

####################################################################
''' Main initialization routine '''
####################################################################

if __name__ == "__main__":
    sys.exit(main())
