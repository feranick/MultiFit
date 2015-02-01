# Multifit v. 20150201b
# Nicola Ferralis <feranick@hotmail.com>
# The entire code is covered by GNU Public License (GPL) v.3

from numpy import *
from lmfit.models import GaussianModel, LorentzianModel, PseudoVoigtModel
from pylab import *
import sys
import os.path
import getopt


def calculate(file, type):
    
    p = Peak(type)
    
    fpeak1 = 1
    fpeak2 = 1
    fpeak3 = 1
    fpeak4 = 0
    fpeak5 = 1
    fpeak6 = 0

    pars = p.peak0.make_params()
    pars['p0_center'].set(1100)
    pars['p0_sigma'].set(45, min=40)
    pars['p0_amplitude'].set(500, min=0)
    if type ==0:
        pars['p0_fraction'].set(0.5, min = 0, max = 1)

    if fpeak1!=0:
        pars.update(p.peak1.make_params())
        pars['p1_center'].set(1250)
        pars['p1_sigma'].set(45, min=40)
        pars['p1_amplitude'].set(1000, min=0)
        if type ==0:
            pars['p1_fraction'].set(0.5, min = 0, max = 1)

    if fpeak2!=0:
        pars.update(p.peak2.make_params())
        pars['p2_center'].set(1330)
        pars['p2_sigma'].set(80, min=40)
        pars['p2_amplitude'].set(5000, min=0)
        if type ==0:
            pars['p2_fraction'].set(0.5, min = 0, max = 1)

    if fpeak3!=0:
        pars.update(p.peak3.make_params())
        pars['p3_center'].set(1420)
        pars['p3_sigma'].set(40, min=20)
        pars['p3_amplitude'].set(300, min=0)
        if type ==0:
            pars['p3_fraction'].set(0.5, min = 0, max = 1)

    if fpeak4!=0:
        pars.update(p.peak4.make_params())
        pars['p4_center'].set(1500)
        pars['p4_sigma'].set(40, min=20)
        pars['p4_amplitude'].set(300, min=0)
        if type ==0:
            pars['p4_fraction'].set(0.5, min = 0, max = 1)

    if fpeak5!=0:
        pars.update(p.peak5.make_params())
        pars['p5_center'].set(1590)
        pars['p5_sigma'].set(40, min=20)
        pars['p5_amplitude'].set(2000, min=0)
        if type ==0:
            pars['p5_fraction'].set(0.5, min = 0, max = 1)

    if fpeak6!=0:
        pars.update(p.peak6.make_params())
        pars['p6_center'].set(1680)
        pars['p6_sigma'].set(40, min=30)
        pars['p6_amplitude'].set(1000, min=0)
        if type ==0:
            pars['p6_fraction'].set(0.5, min = 0, max = 1)

    mod = p.peak0
    if fpeak1!=0:
        mod = mod + p.peak1
    if fpeak2!=0:
        mod = mod + p.peak2
    if fpeak3!=0:
        mod = mod + p.peak3
    if fpeak4!=0:
        mod = mod + p.peak4
    if fpeak5!=0:
        mod = mod + p.peak5
    if fpeak6!=0:
        mod = mod + p.peak6


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

    if (fpeak1 ==1 & fpeak2 ==1 & fpeak5 ==1):
        print('\nD5/G = {:f}'.format(out.best_values['p1_amplitude']/out.best_values['p5_amplitude']))
        print('(D4+D5)/G = {:f}'.format((out.best_values['p0_amplitude']+out.best_values['p1_amplitude'])/out.best_values['p5_amplitude']))
        print('D1/G = {:f}'.format(out.best_values['p2_amplitude']/out.best_values['p5_amplitude']))
        print('Fit type: {:}\n'.format(p.typec))
      
    if (fpeak1 ==1 & fpeak2 ==1 & fpeak5 ==1):
        with open(outfile, "a") as text_file:
            text_file.write('\nD5/G = {:f}'.format(out.best_values['p1_amplitude']/out.best_values['p5_amplitude']))
            text_file.write('\n(D4+D5)/G = {:f}'.format((out.best_values['p0_amplitude']+out.best_values['p1_amplitude'])/out.best_values['p5_amplitude']))
            text_file.write('\nD1/G = {:f}'.format(out.best_values['p2_amplitude']/out.best_values['p5_amplitude']))
            text_file.write('Fit type: {:}\n'.format(self.typec))


    if os.path.isfile(summary) == False:
        header = True
    else:
        header = False

    if (fpeak1 ==1 & fpeak2 ==1 & fpeak5 ==1):
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

    y0 = p.peak0.eval(x = x, **out.best_values)
    plt.plot(x,y0,'g')

    if (fpeak1 ==1):
        y1 = p.peak1.eval(x = x, **out.best_values)
        plt.plot(x,y1,'g',linewidth=2.0)
    if (fpeak2 ==1):
        y2 = p.peak2.eval(x = x, **out.best_values)
        plt.plot(x,y2,'g')
    if (fpeak3 ==1):
        y3 = p.peak3.eval(x = x, **out.best_values)
        plt.plot(x,y3,'g')
    if (fpeak4 ==1):
        y4 = p.peak4.eval(x = x, **out.best_values)
        plt.plot(x,y4,'g')
    if (fpeak5 ==1):
        y5 = p.peak5.eval(x = x, **out.best_values)
        plt.plot(x,y5,'g',linewidth=2.0)
    if (fpeak6 ==1):
        y6 = p.peak6.eval(x = x, **out.best_values)
        plt.plot(x,y6,'g')


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
        if type==0:
            self.peak0 = PseudoVoigtModel(prefix="p0_")
            self.peak1 = PseudoVoigtModel(prefix="p1_")
            self.peak2 = PseudoVoigtModel(prefix="p2_")
            self.peak3 = PseudoVoigtModel(prefix="p3_")
            self.peak4 = PseudoVoigtModel(prefix="p4_")
            self.peak5 = PseudoVoigtModel(prefix="p5_")
            self.peak6 = PseudoVoigtModel(prefix="p6_")
            self.typec = "PVoigt"
        else:
            if type == 1:
                self.peak0 = LorentzianModel(prefix="p0_")
                self.peak1 = LorentzianModel(prefix="p1_")
                self.peak2 = LorentzianModel(prefix="p2_")
                self.peak3 = LorentzianModel(prefix="p3_")
                self.peak4 = LorentzianModel(prefix="p4_")
                self.peak5 = LorentzianModel(prefix="p5_")
                self.peak6 = LorentzianModel(prefix="p6_")
                self.typec = "Lorentz"
            else:
                self.peak0 = GaussianModel(prefix="p0_")
                self.peak1 = GaussianModel(prefix="p1_")
                self.peak2 = GaussianModel(prefix="p2_")
                self.peak3 = GaussianModel(prefix="p3_")
                self.peak4 = GaussianModel(prefix="p4_")
                self.peak5 = GaussianModel(prefix="p5_")
                self.peak6 = GaussianModel(prefix="p6_")
                self.typec = "Gauss"



if __name__ == "__main__":
    sys.exit(main())
