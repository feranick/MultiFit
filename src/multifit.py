# Multifit v. 20150202b
# Nicola Ferralis <feranick@hotmail.com>
# The entire code is covered by GNU Public License (GPL) v.3

from numpy import *
from lmfit.models import GaussianModel, LorentzianModel, PseudoVoigtModel
from pylab import *
import sys
import os.path
import getopt

global NumPeaks
NumPeaks = 6

def calculate(file, type):
    
    p = Peak(type)
    
    fpeak = [None]*(NumPeaks+1)
    fpeak =[1, 1, 1, 1, 0, 1, 0]
    
    pars = p.peak[0].make_params()
    pars['p0_center'].set(1100)
    pars['p0_sigma'].set(45, min=40)
    pars['p0_amplitude'].set(500, min=0)
    if type ==0:
        pars['p0_fraction'].set(0.5, min = 0, max = 1)

    if fpeak[1]!=0:
        pars.update(p.peak[1].make_params())
        pars['p1_center'].set(1250)
        pars['p1_sigma'].set(45, min=40)
        pars['p1_amplitude'].set(1000, min=0)
        if type ==0:
            pars['p1_fraction'].set(0.5, min = 0, max = 1)

    if fpeak[2]!=0:
        pars.update(p.peak[2].make_params())
        pars['p2_center'].set(1330)
        pars['p2_sigma'].set(80, min=40)
        pars['p2_amplitude'].set(5000, min=0)
        if type ==0:
            pars['p2_fraction'].set(0.5, min = 0, max = 1)

    if fpeak[3]!=0:
        pars.update(p.peak[3].make_params())
        pars['p3_center'].set(1420)
        pars['p3_sigma'].set(40, min=20)
        pars['p3_amplitude'].set(300, min=0)
        if type ==0:
            pars['p3_fraction'].set(0.5, min = 0, max = 1)

    if fpeak[4]!=0:
        pars.update(p.peak[4].make_params())
        pars['p4_center'].set(1500)
        pars['p4_sigma'].set(40, min=20)
        pars['p4_amplitude'].set(300, min=0)
        if type ==0:
            pars['p4_fraction'].set(0.5, min = 0, max = 1)

    if fpeak[5]!=0:
        pars.update(p.peak[5].make_params())
        pars['p5_center'].set(1590)
        pars['p5_sigma'].set(40, min=20)
        pars['p5_amplitude'].set(2000, min=0)
        if type ==0:
            pars['p5_fraction'].set(0.5, min = 0, max = 1)

    if fpeak[6]!=0:
        pars.update(p.peak[6].make_params())
        pars['p6_center'].set(1680)
        pars['p6_sigma'].set(40, min=30)
        pars['p6_amplitude'].set(1000, min=0)
        if type ==0:
            pars['p6_fraction'].set(0.5, min = 0, max = 1)

    mod = p.peak[0]

    for i in range (1,NumPeaks+1):
        if fpeak[i]!=0:
            mod = mod + p.peak[i]

    ########################################
    data = loadtxt(file)
    x = data[:, 0]
    y = data[:, 1]

    init = mod.eval(pars, x=x)
    plot(x, y, label='data')
    plot(x, init, 'k--', label='initial')

    out = mod.fit(y, pars,x=x)

    print(out.fit_report(min_correl=0.25))

    #for key in out.best_values:
    #    ex_str = '{:} = {:f}'.format(key, out.best_values[key])
    #    print(ex_str)

    outfile = 'fit_' + file
    summary = 'summary.txt'

    if (fpeak[1] ==1 & fpeak[2] ==1 & fpeak[5] ==1):
        print('\nD5/G = {:f}'.format(out.best_values['p1_amplitude']/out.best_values['p5_amplitude']))
        print('(D4+D5)/G = {:f}'.format((out.best_values['p0_amplitude']+out.best_values['p1_amplitude'])/out.best_values['p5_amplitude']))
        print('D1/G = {:f}'.format(out.best_values['p2_amplitude']/out.best_values['p5_amplitude']))
        print('Fit type: {:}\n'.format(p.typec))
      
    if (fpeak[1] ==1 & fpeak[2] ==1 & fpeak[5] ==1):
        with open(outfile, "a") as text_file:
            text_file.write('\nD5/G = {:f}'.format(out.best_values['p1_amplitude']/out.best_values['p5_amplitude']))
            text_file.write('\n(D4+D5)/G = {:f}'.format((out.best_values['p0_amplitude']+out.best_values['p1_amplitude'])/out.best_values['p5_amplitude']))
            text_file.write('\nD1/G = {:f}'.format(out.best_values['p2_amplitude']/out.best_values['p5_amplitude']))
            text_file.write('Fit type: {:}\n'.format(p.typec))


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

    #plt.plot(x, out.init_fit, 'k--')
    plot(x, out.best_fit, 'r-', label='fit')

    y0 = p.peak[0].eval(x = x, **out.best_values)
    plt.plot(x,y0,'g')


    y = [None]*(NumPeaks + 1)
    for i in range (1,NumPeaks):
        if (fpeak[i] ==1):
            y[i] = p.peak[i].eval(x = x, **out.best_values)
            if (i==1 or i==5):
                plt.plot(x,y[i],'g',linewidth=2.0)
            else:
                plt.plot(x,y[i],'g')

    ### add D5G values to plot

    xlabel('Raman shift [1/cm]')
    ylabel('Intensity [arb. units]')
    legend()
    grid(True)
    #savefig("test.png")
    show()

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
