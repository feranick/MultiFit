# Multifit
# Nicola Ferralis <feranick@hotmail.com>
# The entire code is covered by GNU Public License (GPL) v.3

import openpyxl as px
from numpy import *
from lmfit.models import GaussianModel, LorentzianModel, PseudoVoigtModel
import matplotlib.pyplot as plt
import sys, os.path, getopt

version = '20150213a'
### Define number of total peaks
#global NumPeaks
NumPeaks = 7

def calculate(file, type):
    p = Peak(type)
    fpeak = []
    
    ### Load initialization parameters from xlsx file.
    
    W = px.load_workbook('input_parameters.xlsx', use_iterators = True)
    sheet = W.active
    inval=[]

    for row in sheet.iter_rows():
        for k in row:
            inval.append(k.internal_value)
    inv = resize(inval, [14, NumPeaks+1])

    ### Use this to define qhich peak is active (NOTE: the first needs always to be 1)
    for i in range(1, NumPeaks+1):
        fpeak.extend([int(inv[1,i])])

    ### Initialize parameters for fit.
    pars = p.peak[0].make_params()
    pars['p0_center'].set(inv[2,1], min = inv[3,1], max = inv[4,1] )
    pars['p0_sigma'].set(inv[5,1], min = inv[6,1], max = inv [7,1])
    pars['p0_amplitude'].set(inv[8,1], min=inv[9,1], max = inv[10,1])
    if type ==0:
        pars['p0_fraction'].set(inv[11,1], min = inv[12,1], max = inv[13,1])

    for i in range (1, NumPeaks):
        if fpeak[i]!=0:
            pars.update(p.peak[i].make_params())
            pars['p{:}_center'.format(str(i))].set(inv[2,i+1], min = inv[3,i+1], max = inv[4,i+1])
            pars['p{:}_sigma'.format(str(i))].set(inv[5,i+1], min = inv[6,i+1], max = inv [7,i+1])
            pars['p{:}_amplitude'.format(str(i))].set(inv[8,i+1], min=inv[9,i+1], max = inv[10,i+1])
            if type ==0:
                pars['p{:}_fraction'.format(str(i))].set(inv[11,i+1], min = inv[12,i+1], max = inv[13,i+1])

    ### Add relevant peak to fitting procedure.
    mod = p.peak[0]
    for i in range (1,NumPeaks):
        if fpeak[i]!=0:
            mod = mod + p.peak[i]

    ### Load data
    data = loadtxt(file)
    x = data[:, 0]
    y = data[:, 1]

    ### Initialize and plot initial prefitting curves
    init = mod.eval(pars, x=x)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(x, y, label='data')
    ax.plot(x, init, 'k--', label='initial')

    ### Perform fitting and display report
    print(' Running Fit...')
    out = mod.fit(y, pars,x=x)
    print(' Done! \n')
    print(out.fit_report(min_correl=0.25))

    ### Save individual fitting results
    outfile = 'fit_' + file
    ### Save summary fitting results
    #summary = 'summary.txt'
    summary = 'summary.xlsx'
    if os.path.isfile(summary) == False:
        header = True
    else:
        header = False

    if (fpeak[1] == 1 & fpeak[2] == 1 & fpeak[5] == 1):
        print('\nD5/G = {:f}'.format(out.best_values['p1_amplitude']/out.best_values['p5_amplitude']))
        print('(D4+D5)/G = {:f}'.format((out.best_values['p0_amplitude']+out.best_values['p1_amplitude'])/out.best_values['p5_amplitude']))
        print('D1/G = {:f}'.format(out.best_values['p2_amplitude']/out.best_values['p5_amplitude']))
        if type ==0:
            print('G: {:f}% Gaussian'.format(out.best_values['p5_fraction']*100))
        print('Fit type: {:}\n'.format(p.typec))
      
        with open(outfile, "a") as text_file:
            text_file.write('\nD5/G = {:f}'.format(out.best_values['p1_amplitude']/out.best_values['p5_amplitude']))
            text_file.write('\n(D4+D5)/G = {:f}'.format((out.best_values['p0_amplitude']+out.best_values['p1_amplitude'])/out.best_values['p5_amplitude']))
            text_file.write('\nD1/G = {:f}'.format(out.best_values['p2_amplitude']/out.best_values['p5_amplitude']))
            if type ==0:
                text_file.write('\nG %Gaussian: {:f}'.format(out.best_values['p5_fraction']))
            text_file.write('\nFit type: {:}\n'.format(p.typec))

        '''
        ### Use this for summary in ASCII
        with open(summary, "a") as sum_file:
            if header == True:
                sum_file.write('File\tiD1\tiD4\tiD5\tiG\twG\tD5G\t(D4+D5)/G\tD1/G\t%Gaussian\tfit\n')
            sum_file.write('{:}\t'.format(file))
            sum_file.write('{:f}\t'.format(out.best_values['p2_amplitude']))
            sum_file.write('{:f}\t'.format(out.best_values['p0_amplitude']))
            sum_file.write('{:f}\t'.format(out.best_values['p1_amplitude']))
            sum_file.write('{:f}\t'.format(out.best_values['p5_amplitude']))
            sum_file.write('{:f}\t'.format(out.best_values['p5_sigma']*2))
            sum_file.write('{:f}\t'.format(out.best_values['p1_amplitude']/out.best_values['p5_amplitude']))
            sum_file.write('{:f}\t'.format((out.best_values['p0_amplitude']+out.best_values['p1_amplitude'])/out.best_values['p5_amplitude']))
            sum_file.write('{:f}\t'.format(out.best_values['p2_amplitude']/out.best_values['p5_amplitude']))
            if type ==0:
                sum_file.write('{:f}\t'.format(out.best_values['p5_fraction']))
            else:
                sum_file.write('{:}\t'.format(type-1))
            sum_file.write('{:}\n'.format(p.typec))
        '''

        ### Use this for summary in XLSX
        if header == True:
            WW=px.Workbook()
            pp=WW.active
            pp.title='Summary'
            summaryHeader = ['File', 'iD1', 'iD4', 'iD5', 'iG', 'wG', 'D5G', '(D4+D5)/G', 'D1/G', 'D5 %Gaussian','D1 %Gaussian', 'G %Gaussian', 'Fit']
            pp.append(summaryHeader)
            WW.save(summary)

        WW = px.load_workbook(summary)
        pp = WW.active

        summaryResults = ['{:}'.format(file), '{:f}'.format(out.best_values['p2_amplitude']), \
                          '{:f}'.format(out.best_values['p0_amplitude']),
                          '{:f}'.format(out.best_values['p1_amplitude']), \
                          '{:f}'.format(out.best_values['p5_amplitude']), \
                          '{:f}'.format(out.best_values['p5_sigma']*2), \
                          '{:f}'.format(out.best_values['p1_amplitude']/out.best_values['p5_amplitude']), \
                          '{:f}'.format((out.best_values['p0_amplitude']+out.best_values['p1_amplitude'])/out.best_values['p5_amplitude']), \
                          '{:f}'.format(out.best_values['p2_amplitude']/out.best_values['p5_amplitude'])]
        if type ==0:
            summaryResults.extend(['{:f}'.format(out.best_values['p1_fraction']), \
                                   '{:f}'.format(out.best_values['p2_fraction']), \
                                   '{:f}'.format(out.best_values['p5_fraction'])])
        else:
            summaryResults.extend(['{:}'.format(type-1), '{:}'.format(type-1), '{:}'.format(type-1)])
        summaryResults.extend([p.typec])
        pp.append(summaryResults)
        WW.save(summary)

    ### Plot optimal fit and individial components
    ax.plot(x, out.best_fit, 'r-', label='fit')
    y0 = p.peak[0].eval(x = x, **out.best_values)
    ax.plot(x,y0,'g')
    y = [None]*(NumPeaks + 1)
    for i in range (1,NumPeaks):
        if (fpeak[i] ==1):
            y[i] = p.peak[i].eval(x = x, **out.best_values)
            if (i==1 or i==5):
                ax.plot(x,y[i],'g',linewidth=2.0)
            else:
                ax.plot(x,y[i],'g')

    ax.text(0.05, 0.9, 'D5/G = {:f}'.format(out.best_values['p1_amplitude']/out.best_values['p5_amplitude']), transform=ax.transAxes)
    ax.text(0.05, 0.9, 'Fit type: {:}\n'.format(p.typec), transform=ax.transAxes)
    
    plt.xlabel('Raman shift [1/cm]')
    plt.ylabel('Intensity [arb. units]')
    plt.legend()
    plt.grid(True)
    print('*** Close plot to quit ***\n')
    plt.show()


###################

def main():
    print('\n******************************')
    print(' MultiFit v.' + version)
    print('******************************\n')

    try:
        opts, args = getopt.getopt(sys.argv[1:], "ho:v", ["help", "output="])
    except getopt.GetoptError:
        # print help information and exit:
        usage()
        sys.exit(2)
    
    #file = 'PPRG-498_DG_fit_5.txt'
    file = str(sys.argv[1])
    type = int(sys.argv[2])

    calculate(file, type)

class Peak:
    ### Define the typology of the peak
    def __init__(self, type):
        
        self.peak= [None]*(NumPeaks)
        
        if type==0:
            for i in range (0,NumPeaks):
                self.peak[i] = PseudoVoigtModel(prefix="p"+ str(i) +"_")
            self.typec = "PVoigt"
        else:
            if type == 1:
                for i in range (0,NumPeaks):
                    self.peak[i] = GaussianModel(prefix="p"+ str(i) +"_")
                self.typec = "Gauss"
            else:
                for i in range (0,NumPeaks):
                    self.peak[i] = LorentzianModel(prefix="p"+ str(i) +"_")
                self.typec = "Lorentz"

if __name__ == "__main__":
    sys.exit(main())
