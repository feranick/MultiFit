# Multifit v. 20150125a
# Nicola Ferralis <feranick@hotmail.com>
# The entire code is covered by GNU Public License (GPL) v.3

from numpy import *
from lmfit.models import GaussianModel, LorentzianModel, PseudoVoigtModel
from pylab import *
import sys
import os.path
import getopt


def main():
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ho:v", ["help", "output="])
    except getopt.GetoptError:
        # print help information and exit:
        usage()
        sys.exit(2)

    #file = 'PPRG-498_DG_fit_5.txt'
    file = str(sys.argv[1])
    outfile = 'fit_' + file
    summary = 'summary.txt'

    type = int(sys.argv[2])
    #type = 0
    fpeak6 = 0

    if type==0:
        typec = "Lor"
        peak0 = LorentzianModel(prefix="p0_")
        peak1 = LorentzianModel(prefix="p1_")
        peak2 = LorentzianModel(prefix="p2_")
        peak3 = LorentzianModel(prefix="p3_")
        peak4 = LorentzianModel(prefix="p4_")
        peak5 = LorentzianModel(prefix="p5_")
        if fpeak6!=0:
            peak6 = LorentzianModel(prefix="p6_")
    else:
        if type == 1:
            typec = "Gauss"
            peak0 = GaussianModel(prefix="p0_")
            peak1 = GaussianModel(prefix="p1_")
            peak2 = GaussianModel(prefix="p2_")
            peak3 = GaussianModel(prefix="p3_")
            peak4 = GaussianModel(prefix="p4_")
            peak5 = GaussianModel(prefix="p5_")
            if fpeak6!=0:
                peak6 = GaussianModel(prefix="p6_")
        else:
            typec = "PVoigt"
            peak0 = PseudoVoigtModel(prefix="p0_")
            peak1 = PseudoVoigtModel(prefix="p1_")
            peak2 = PseudoVoigtModel(prefix="p2_")
            peak3 = PseudoVoigtModel(prefix="p3_")
            peak4 = PseudoVoigtModel(prefix="p4_")
            peak5 = PseudoVoigtModel(prefix="p5_")
            if fpeak6!=0:
                peak6 = PseudoVoigtModel(prefix="p6_")

    pars = peak0.make_params()
    pars['p0_center'].set(1100)
    pars['p0_sigma'].set(45, min=40)
    pars['p0_amplitude'].set(500, min=0)
    if type ==3:
        pars['p0_fraction'].set(0.3, min = 0)

    pars.update(peak1.make_params())
    pars['p1_center'].set(1250)
    pars['p1_sigma'].set(45, min=40)
    pars['p1_amplitude'].set(1000, min=0)
    if type ==3:
        pars['p1_fraction'].set(0.3, min = 0)

    pars.update(peak2.make_params())
    pars['p2_center'].set(1330)
    pars['p2_sigma'].set(80, min=40)
    pars['p2_amplitude'].set(5000, min=0)
    if type ==3:
        pars['p2_fraction'].set(0.3, min = 0)

    pars.update(peak3.make_params())
    pars['p3_center'].set(1420)
    pars['p3_sigma'].set(40, min=20)
    pars['p3_amplitude'].set(300, min=0)
    if type ==3:
        pars['p3_fraction'].set(0.3, min = 0)

    pars.update(peak4.make_params())
    pars['p4_center'].set(1500)
    pars['p4_sigma'].set(40, min=20)
    pars['p4_amplitude'].set(300, min=0)
    if type ==3:
        pars['p4_fraction'].set(0.3, min = 0)

    pars.update(peak5.make_params())
    pars['p5_center'].set(1590)
    pars['p5_sigma'].set(40, min=20)
    pars['p5_amplitude'].set(2000, min=0)
    if type ==3:
        pars['p5_fraction'].set(0.3, min = 0)

    if fpeak6!=0:
        pars.update(peak6.make_params())
        pars['p6_center'].set(1680)
        pars['p6_sigma'].set(40, min=30)
        pars['p6_amplitude'].set(1000, min=0)
        if type ==3:
            pars['p6_fraction'].set(0.3, min = 0)

    if fpeak6!=0:
        mod = peak0 + peak1 + peak2 + peak3 + peak4 + peak5 + peak6
    else:
        mod = peak0 + peak1 + peak2 + peak3 + peak5



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

    print('\nD5/G = {:f}'.format(out.best_values['p1_amplitude']/out.best_values['p5_amplitude']))
    print('(D4+D5)/G = {:f}'.format((out.best_values['p0_amplitude']+out.best_values['p1_amplitude'])/out.best_values['p5_amplitude']))
    print('D1/G = {:f}\n'.format(out.best_values['p2_amplitude']/out.best_values['p5_amplitude']))
      

    with open(outfile, "a") as text_file:
        text_file.write('\nD5/G = {:f}'.format(out.best_values['p1_amplitude']/out.best_values['p5_amplitude']))
        text_file.write('\n(D4+D5)/G = {:f}'.format((out.best_values['p0_amplitude']+out.best_values['p1_amplitude'])/out.best_values['p5_amplitude']))
        text_file.write('\nD1/G = {:f}\n'.format(out.best_values['p2_amplitude']/out.best_values['p5_amplitude']))


    if os.path.isfile(summary) == False:
        header = True
    else:
        header = False

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
        sum_file.write('{:}\n'.format(typec))

    #plt.plot(x, out.init_fit, 'k--')
    plot(x, out.best_fit, 'r-', label='fit')

    y0 = peak0.eval(x = x, **out.best_values)
    y1 = peak1.eval(x = x, **out.best_values)
    y2 = peak2.eval(x = x, **out.best_values)
    y3 = peak3.eval(x = x, **out.best_values)
    y4 = peak4.eval(x = x, **out.best_values)
    y5 = peak5.eval(x = x, **out.best_values)
    #y6 = peak6.eval(x = x, **out.best_values)


    plt.plot(x,y0,'g')
    plt.plot(x,y1,'g')
    plt.plot(x,y2,'g')
    plt.plot(x,y3,'g')
    plt.plot(x,y4,'g')
    plt.plot(x,y5,'g')
    #plt.plot(x,y6,'g')

    ### add D5G values to plot

    xlabel('Raman shift [1/cm]')
    ylabel('Intensity [arb. units]')
    legend()
    grid(True)
    #savefig("test.png")
    show()

if __name__ == "__main__":
    sys.exit(main())
