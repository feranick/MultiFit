# Multifit v. 20150206b
# Nicola Ferralis <feranick@hotmail.com>
# The entire code is covered by GNU Public License (GPL) v.3

from numpy import *
from lmfit.models import GaussianModel, LorentzianModel, PseudoVoigtModel
import matplotlib.pyplot as plt
import sys, os.path, getopt

### Define number of total peaks
global NumPeaks
NumPeaks = 6

def calculate(file, type):
    p = Peak(type)
    fpeak = [None]*(NumPeaks+1)
    
    ### Use this to define qhich peak is active (NOTE: the first needs always to be 1)
    fpeak =[1, 1, 1, 1, 0, 1, 0]
    
    ### Define the relevant parameters for each peak here.
    
    ### D4
    pc = [1100]     # Center
    ps = [45]       # Sigma
    ps_min = [40]   # Sigma minimum
    pa = [500]      # Amplitde
    pa_min = [0]    # Amplitde minimum
    pf = [0.5]      # Factor (PseudoVoigt)
    pf_min = [0]    # Full Gaussian
    pf_max = [1]    # Full Lorentzian

    ### D5
    pc.extend([1250])
    ps.extend([45])
    ps_min.extend([40])
    pa.extend([1000])
    pa_min.extend([0])
    pf.extend([0.5])
    pf_min.extend([0])
    pf_max.extend([1])

    ### D1
    pc.extend([1330])
    ps.extend([80])
    ps_min.extend([40])
    pa.extend([5000])
    pa_min.extend([0])
    pf.extend([0.5])
    pf_min.extend([0])
    pf_max.extend([1])
    
    ### D3a
    pc.extend([1420])
    ps.extend([40])
    ps_min.extend([20])
    pa.extend([300])
    pa_min.extend([0])
    pf.extend([0.5])
    pf_min.extend([0])
    pf_max.extend([1])
    
    ### D3b
    pc.extend([1500])
    ps.extend([40])
    ps_min.extend([20])
    pa.extend([300])
    pa_min.extend([0])
    pf.extend([0.5])
    pf_min.extend([0])
    pf_max.extend([1])
    
    ### G
    pc.extend([1590])
    ps.extend([40])
    ps_min.extend([20])
    pa.extend([2000])
    pa_min.extend([0])
    pf.extend([0.5])
    pf_min.extend([0])
    pf_max.extend([1])
    
    ### D2
    pc.extend([1680])
    ps.extend([40])
    ps_min.extend([30])
    pa.extend([1000])
    pa_min.extend([0])
    pf.extend([0.5])
    pf_min.extend([0])
    pf_max.extend([1])


    pars = p.peak[0].make_params()
    pars['p0_center'].set(pc[0])
    pars['p0_sigma'].set(ps[0], min=ps_min[0])
    pars['p0_amplitude'].set(pa[0], min=ps_min[0])
    if type ==0:
        pars['p0_fraction'].set(pf[0], min = pf_min[0], max = pf_max[0])


    for i in range (1, NumPeaks+1):
        if fpeak[i]!=0:
            pars.update(p.peak[i].make_params())
            pars['p{:}_center'.format(str(i))].set(pc[i])
            pars['p{:}_sigma'.format(str(i))].set(ps[i], min=ps_min[i])
            pars['p{:}_amplitude'.format(str(i))].set(pa[i], min=pa_min[i])
            if type ==0:
                pars['p{:}_fraction'.format(str(i))].set(pf[0], min = pf_min[i], max = pf_max[i])


    ### Add relevant peak to fittong procedure.
    mod = p.peak[0]
    for i in range (1,NumPeaks+1):
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

    if (fpeak[1] ==1 & fpeak[2] ==1 & fpeak[5] ==1):
        print('\nD5/G = {:f}'.format(out.best_values['p1_amplitude']/out.best_values['p5_amplitude']))
        print('(D4+D5)/G = {:f}'.format((out.best_values['p0_amplitude']+out.best_values['p1_amplitude'])/out.best_values['p5_amplitude']))
        print('D1/G = {:f}'.format(out.best_values['p2_amplitude']/out.best_values['p5_amplitude']))
        print('G: {:f}% Gaussian'.format(out.best_values['p5_fraction']*100))
        print('Fit type: {:}\n'.format(p.typec))
      
    if (fpeak[1] ==1 & fpeak[2] ==1 & fpeak[5] ==1):
        with open(outfile, "a") as text_file:
            text_file.write('\nD5/G = {:f}'.format(out.best_values['p1_amplitude']/out.best_values['p5_amplitude']))
            text_file.write('\n(D4+D5)/G = {:f}'.format((out.best_values['p0_amplitude']+out.best_values['p1_amplitude'])/out.best_values['p5_amplitude']))
            text_file.write('\nD1/G = {:f}'.format(out.best_values['p2_amplitude']/out.best_values['p5_amplitude']))
            text_file.write('G %Gaussian: {:f}'.format(out.best_values['p5_fraction']))
            text_file.write('Fit type: {:}\n'.format(p.typec))

    ### Save summary fitting results
    summary = 'summary.txt'
    if os.path.isfile(summary) == False:
        header = True
    else:
        header = False

    if (fpeak[1] ==1 & fpeak[2] ==1 & fpeak[5] ==1):
        with open(summary, "a") as sum_file:
            if header == True:
                sum_file.write('File\tiD1\tiD4\tiD5\tiG\twG\tD5G\t(D4+D5)/G\tD1/G\tfit\n')
            sum_file.write('{:}\t'.format(file))
            sum_file.write('{:f}\t'.format(out.best_values['p2_amplitude']))
            sum_file.write('{:f}\t'.format(out.best_values['p0_amplitude']))
            sum_file.write('{:f}\t'.format(out.best_values['p1_amplitude']))
            sum_file.write('{:f}\t'.format(out.best_values['p5_amplitude']))
            sum_file.write('{:f}\t'.format(out.best_values['p5_sigma']*2))
            sum_file.write('{:f}\t'.format(out.best_values['p1_amplitude']/out.best_values['p5_amplitude']))
            sum_file.write('{:f}\t'.format((out.best_values['p0_amplitude']+out.best_values['p1_amplitude'])/out.best_values['p5_amplitude']))
            sum_file.write('{:f}\t'.format(out.best_values['p2_amplitude']/out.best_values['p5_amplitude']))
            sum_file.write('{:}\n'.format(p.typec))

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
        
        self.peak= [None]*(NumPeaks+1)
        
        if type==0:
            for i in range (0,NumPeaks+1):
                self.peak[i] = PseudoVoigtModel(prefix="p"+ str(i) +"_")
            self.typec = "PVoigt"
        else:
            if type == 1:
                for i in range (0,NumPeaks+1):
                    self.peak[i] = LorentzianModel(prefix="p"+ str(i) +"_")
                self.typec = "Lorentz"
            else:
                for i in range (0,NumPeaks+1):
                    self.peak[i] = GaussianModel(prefix="p"+ str(i) +"_")
                self.typec = "Gauss"

if __name__ == "__main__":
    sys.exit(main())
