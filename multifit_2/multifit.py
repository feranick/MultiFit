#! /usr/bin/env python

###=============================================================
### Multifit 2
### Nicola Ferralis <feranick@hotmail.com>
### The entire code is covered by GNU Public License (GPL) v.3
###=============================================================

### Uncomment this if for headless servers.
#import matplotlib
#matplotlib.use('Agg')
### ---------------------------------------
from numpy import *
from lmfit.models import GaussianModel, LorentzianModel, PseudoVoigtModel, VoigtModel
import matplotlib.pyplot as plt
import sys, os.path, getopt, glob, csv
from os.path import exists
from multiprocessing import Pool
import multiprocessing as mp

####################################################################
''' Program definitions and configuration variables '''
####################################################################
class defPar:
    version = '2-20150319a'
    ### Define number of total peaks (do not change: this is read from file)
    NumPeaks = 0
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
            defPar.NumPeaks = len(row)-1
            row = [nulStrConvDigit(entry) for entry in row]
            inval.append(row)
            numRows +=1
        inputFile.close()
    inv = resize(inval, [numRows, defPar.NumPeaks+1])
    fpeak = []

    # define active peaks
    for i in range(1, defPar.NumPeaks+1):
        fpeak.extend([int(inv[1,i])])

	p = Peak(type)
    print (' Fitting with ' + str(defPar.NumPeaks) + ' (' + p.typec + ') peaks')
    
    ### Initialize parameters for fit.
    pars = p.peak[0].make_params()
    for i in range (0, defPar.NumPeaks):
        if fpeak[i]!=0:

            fac = 2
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
    mod = p.peak[0]
    for i in range (1,defPar.NumPeaks):
        if fpeak[i]!=0:
            mod += p.peak[i]

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
    plotfile = os.path.splitext(file)[0] + '_fit.png'   # Save plot as image

    if os.path.isfile(defPar.summary) == False:
        header = True
    else:
        header = False
        print('\nFit successful: ' + str(out.success))

        d5g = out.best_values['p1_amplitude']/out.best_values['p5_amplitude']
        d4d5g = (out.best_values['p0_amplitude']+out.best_values['p1_amplitude'])/out.best_values['p5_amplitude']
        d1g = out.best_values['p2_amplitude']/out.best_values['p5_amplitude']

    if (processMap == False):
        if (fpeak[1] == 1 & fpeak[2] == 1 & fpeak[5] == 1):
            print('D5/G = {:f}'.format(d5g))
            print('(D4+D5)/G = {:f}'.format(d4d5g))
            print('D1/G = {:f}'.format(d1g))
            if type ==0:
                print('G: {:f}% Gaussian'.format(out.best_values['p5_fraction']*100))
            print('Fit type: {:}'.format(p.typec))
            print('Chi-square: {:}'.format(out.chisqr))
            print('Reduced Chi-square: {:}\n'.format(out.redchi))

            ### Uncomment to enable saving results of each fit in a separate file.
            '''
                with open(outfile, "a") as text_file:
                text_file.write('\nD5/G = {:f}'.format(d5g))
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
            d5g, d4d5g, 0, \
            out.best_values['p2_amplitude'], \
            out.best_values['p0_amplitude'], \
            out.best_values['p1_amplitude'], \
            out.best_values['p5_amplitude'], \
            out.best_values['p5_sigma']*2, \
            d1g ]
    if type ==0:
        summaryFile.extend([out.best_values['p1_fraction'], \
                        out.best_values['p2_fraction'], \
                        out.best_values['p2_fraction']])
    else:
        for i in range(0,3):
            summaryFile.extend([type-1])
    summaryFile.extend([p.typec, out.chisqr, out.redchi, out.success, \
                    x1, y1, lab])

    with open(defPar.summary, "a") as sum_file:
        csv_out=csv.writer(sum_file)
        csv_out.writerow(summaryFile)
        sum_file.close()
    
    if(processMap == True):
        with open(os.path.splitext(file)[0] + '_map.csv', "a") as coord_file:
            coord_file.write('{:},'.format(x1))
            coord_file.write('{:},'.format(y1))
            if (out.success == True and out.redchi < defPar.redchi):
                coord_file.write('{:}\n'.format(d5g))
            else:
                coord_file.write('{:}\n'.format(defPar.outliar))
            coord_file.close()
    else:
        ### Plot optimal fit and individial components
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(x, y, label='data')
        if(defPar.initCurve == True):
            ax.plot(x, init, 'k--', label='initial')
        
        ax.plot(x, out.best_fit, 'r-', label='fit')
        y0 = p.peak[0].eval(x = x, **out.best_values)
        ax.plot(x,y0,'g')
        y = [None]*(defPar.NumPeaks + 1)
        for i in range (1,defPar.NumPeaks):
            if (fpeak[i] ==1):
                y[i] = p.peak[i].eval(x = x, **out.best_values)
                if (i==1 or i==5):
                    ax.plot(x,y[i],'g',linewidth=2.0)
                else:
                    ax.plot(x,y[i],'g')

        ax.text(0.05, 0.875, 'Fit type: {:}\nD5/G = {:f}\nRed. Chi sq: {:}'.format( \
                                p.typec, \
                                d5g, out.redchi), transform=ax.transAxes)

        plt.xlabel('Raman shift [1/cm]')
        plt.ylabel('Intensity [arb. units]')
        plt.title(file)
        plt.legend()
        plt.grid(True)
        plt.savefig(plotfile)  # Save plot
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
    print('\n******************************')
    print(' MultiFit v.' + defPar.version)
    print('******************************')

    try:
        opts, args = getopt.getopt(sys.argv[1:], "bftmitph:", ["batch", "file", "type", "map", "input-par", "test", "plot", "help"])
    except getopt.GetoptError:
        # print help information and exit:
        usage()
        sys.exit(2)

    # If parameter file not present, make one
    if not exists(defPar.inputParFile):
        print '\n Init parameter not found. Generating a new one...'
        genInitPar()

    # If summary file is not present, make it and fill header
    makeHeaderSummary()

    if(defPar.multiproc == True):
        print('\n Multiprocessing enabled: ' + str(mp.cpu_count()) + ' CPUs\n')
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
                p = Pool(mp.cpu_count())
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


        elif o in ("-p", "--plot"):
            if(len(sys.argv) < 3):
                if(defPar.multiproc == True):
                    p = Pool(mp.cpu_count())
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
            if(defPar.multiproc == True):
                p = Pool(mp.cpu_count())
                for i in range (1, rm.num_lines):
                    p.apply_async(calculate, args=(rm.x, rm.y[i], rm.x1[i], rm.y1[i], file, type, True, False, ''))
                p.close()
                p.join()
            #map.draw(os.path.splitext(file)[0] + '_map.txt', True)

            else:
                for i in range (1, rm.num_lines):
                    calculate(rm.x, rm.y[i], rm.x1[i], rm.y1[i], file, type, True, False, '')
                #map.draw(os.path.splitext(file)[0] + '_map.txt', True)

        elif o in ("-t", "--test"):
            file = str(sys.argv[2])
            map = Map()
            #map.readCoord(os.path.splitext(file)[0] + '_map.txt')
            map.draw(os.path.splitext(file)[0] + '_map.txt', True)

        elif o in ("-i", "--input-par"):
            genInitPar()

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
        
        self.peak= [None]*(defPar.NumPeaks)
        
        if type==0:
            for i in range (0,defPar.NumPeaks):
                self.peak[i] = PseudoVoigtModel(prefix="p"+ str(i) +"_")
            self.typec = "PseudoVoigt"
        elif type == 1:
            for i in range (0,defPar.NumPeaks):
                self.peak[i] = GaussianModel(prefix="p"+ str(i) +"_")
            self.typec = "Gauss"
        elif type == 2:
            for i in range (0,defPar.NumPeaks):
                self.peak[i] = LorentzianModel(prefix="p"+ str(i) +"_")
            self.typec = "Lorentz"
        elif type ==3:
            for i in range (0,defPar.NumPeaks):
                self.peak[i] = VoigtModel(prefix="p"+ str(i) +"_")
            self.typec = "Voigt"
        else:
            print("Warning: type undefined. Using PseudoVoigt")
            for i in range (0,defPar.NumPeaks):
                self.peak[i] = PseudoVoigtModel(prefix="p"+ str(i) +"_")
            self.typec = "PVoigt"

####################################################################
''' Routine to generate initialization parameter file '''
####################################################################

def genInitPar():
    if exists(defPar.inputParFile):
        print(' Input parameter file: ' + defPar.inputParFile + ' already exists\n')
        sys.exit(2)
    else:
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

        print(' Input paramters saved in: ' + defPar.inputParFile)


####################################################################
''' Make header, if absent, for the summary file '''
####################################################################

def makeHeaderSummary():
    if os.path.isfile(defPar.summary) == False:
        summaryHeader = ['File','D5G','(D4+D5)/G','HC','iD1','iD4',\
                         'iD5','iG','wG','D1/G','D5%Gaussian', \
                         'D1%Gaussian','G%Gaussianfit','Fit-type', \
                         'Chi-square','red-chi-sq','Fit-OK','x1','y1', \
                         'label']
        with open(defPar.summary, "a") as sum_file:
            csv_out=csv.writer(sum_file)
            csv_out.writerow(summaryHeader)
            sum_file.close()


####################################################################
''' Lists the program usage '''
####################################################################

def usage():
    print('Usage: \n\n Single file:')
    print(' python multifit.py -f filename n\n')
    print(' Batch processing:')
    print(' python multifit.py -b n\n')
    print(' Map (acquired with horiba LabSpec5): ')
    print(' python multifit.py -m filename n\n')
    print(' Create and save plot of data only (no fit): ')
    print(' python multifit.py -p filename \n')
    print(' Create and save plot of batch data (no fit): ')
    print(' python multifit.py -p \n')
    print(' Create new input paramter file (xlsx): ')
    print(' python multifit.py -i \n')
    print(' n = 0: PseudoVoigt 1: Gaussian 2: Lorentzian 3: Voigt\n')


####################################################################
''' Add blank line at the end of the summary spreadsheet '''
####################################################################

def addBlankLine(file):
    try:
        with open(file, "a") as sum_file:
            sum_file.write('\n')
    except:
        print "File busy!"


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
    pngData = os.path.splitext(file)[0] + '.png'   # Save plot as image
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(x, y, label='data')
    plt.xlabel('Raman shift [1/cm]')
    plt.ylabel('Intensity [arb. units]')
    plt.title(file)
    #plt.legend()
    plt.grid(True)
    plt.savefig(pngData)  # Save plot
    if(showPlot == True):
        print('*** Close plot to quit ***\n')
        plt.show()
    plt.close()


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
#fig = plt.figure()
#ax = fig.add_subplot(111, projection='3d')

#p = ax.pcolor(self.x, self.y, self.z, cmap='Spectral', vmin=min(self.z), vmax=max(self.z))
#fig.colorbar(p, ax=ax)
#surf = ax.plot_trisurf(self.x, self.y, self.z, cmap=cm.jet, linewidth=0)
#fig.colorbar(surf)

#ax.xaxis.set_major_locator(MaxNLocator(5))
#ax.yaxis.set_major_locator(MaxNLocator(6))
#ax.zaxis.set_major_locator(MaxNLocator(5))
#fig.tight_layout()

#plt.xlabel('[um]')
#plt.ylabel('[um]')
#fig.savefig('map.png')  # Save plot
#if(showplot == True):
#    print('*** Close plot to quit ***\n')
#    plt.show()



####################################################################
''' Main initialization routine '''
####################################################################

if __name__ == "__main__":
    sys.exit(main())
