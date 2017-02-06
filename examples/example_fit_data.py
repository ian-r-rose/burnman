# This file is part of BurnMan - a thermoelastic and thermodynamic toolkit for the Earth and Planetary Sciences
# Copyright (C) 2012 - 2015 by the BurnMan team, released under the GNU
# GPL v2 or later.


"""

example_fit_data
----------------

This example demonstrates BurnMan's functionality to fit various mineral physics data to
an EoS of the user's choice. 

Please note also the separate file example_fit_eos.py, which deals specifically with 
PVT fitting as a special case.

teaches:
- least squares fitting

"""
from __future__ import absolute_import
from __future__ import print_function
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as opt

# hack to allow scripts to be placed in subdirectories next to burnman:
if not os.path.exists('burnman') and os.path.exists('../burnman'):
    sys.path.insert(1, os.path.abspath('..'))

import burnman

if __name__ == "__main__":


    # 1) Fitting standard enthalpy and heat capacity to enthalpy data
    per_SLB = burnman.minerals.SLB_2011.periclase()
    per_HP = burnman.minerals.HP_2011_ds62.per()
    per_opt = burnman.minerals.HP_2011_ds62.per() # this is the mineral we'll optimise


    # Load some example enthalpy data
    TH_data = np.loadtxt('../burnman/data/input_fitting/Victor_Douglas_1963_deltaH_MgO.dat')
    per_HP.set_state(1.e5, 298.15)
    PTH_data = np.array([TH_data[:,0]*0. + 1.e5, TH_data[:,0], TH_data[:,2]*4.184 + per_HP.H]).T
    nul = TH_data[:,0]*0.
    PTH_covariances = np.array([[nul, nul, nul], [nul, TH_data[:,1], nul], [nul, nul, np.power(TH_data[:,2]*4.184*0.0004, 2.)]]).T

    per_opt.params['S_0'] = 6.439*4.184
    model = burnman.tools.fit_PTp_data(mineral = per_opt,
                                       p_flags = 'H',
                                       fit_params = ['H_0', 'Cp'],
                                       PTp = PTH_data,
                                       PTp_covariances = PTH_covariances,
                                       max_lm_iterations = 10,
                                       verbose = False)

    print('Optimised values:')
    params = ['H_0', 'Cp_a', 'Cp_b', 'Cp_c', 'Cp_d']
    burnman.tools.pretty_print_values(model.popt, model.pcov, params)
    print('')
    
    # Corner plot
    fig=burnman.nonlinear_fitting.corner_plot(model.popt, model.pcov, params)
    plt.show()

    # Plot models
    temperatures = np.linspace(200., 2000., 101)
    pressures = np.array([298.15] * len(temperatures))
    plt.plot(temperatures, per_HP.evaluate(['heat_capacity_p'], pressures, temperatures)[0], linestyle='--', label='HP')
    plt.plot(temperatures, per_SLB.evaluate(['heat_capacity_p'], pressures, temperatures)[0], linestyle='--', label='SLB')
    plt.plot(temperatures, per_opt.evaluate(['heat_capacity_p'], pressures, temperatures)[0], label='Optimised fit')

    plt.legend(loc='lower right')
    plt.xlim(0., temperatures[-1])
    plt.xlabel('Temperature (K)')
    plt.ylabel('Heat capacity (J/K/mol)')
    plt.show()



    # 2) Fitting shear modulus and its derivative to shear wave velocity data
    
    # First, read in the data from file and convert to SI units.
    PTp_data = np.loadtxt('../burnman/data/input_minphys/Murakami_perovskite.txt')
    PTp_data[:,0] = PTp_data[:,0]*1.e9
    PTp_data[:,2] = PTp_data[:,2]*1.e3

    # Make the test mineral
    mg_perovskite_test = burnman.Mineral()
    mg_perovskite_test.params = {'V_0': 24.45e-6,
                                 'K_0': 281.e9,
                                 'Kprime_0': 4.1,
                                 'molar_mass': .10,
                                 'G_0': 200.e9,
                                 'Gprime_0': 2.}


    def best_fit():
        return burnman.tools.fit_PTp_data(mineral = mg_perovskite_test,
                                          p_flags = 'shear_wave_velocity',
                                          fit_params = ['G_0', 'Gprime_0'],
                                          PTp = PTp_data,
                                          verbose = False)

    pressures = np.linspace(1.e5, 150.e9, 101)
    temperatures = pressures*0. + 300.

    # Fit to the second order Birch-Murnaghan EoS
    mg_perovskite_test.set_method("bm2")
    fitted_eos = best_fit()
    print('2nd order fit:')
    burnman.tools.pretty_print_values(fitted_eos.popt, fitted_eos.pcov, fitted_eos.fit_params)
    model_vs_2nd_order_correct = mg_perovskite_test.evaluate(['shear_wave_velocity'],
                                                             pressures, temperatures)[0]
    mg_perovskite_test.set_method("bm3")
    model_vs_2nd_order_incorrect = mg_perovskite_test.evaluate(['shear_wave_velocity'],
                                                               pressures, temperatures)[0]
    print('')
    

    # Fit to the third order Birch-Murnaghan EoS

    mg_perovskite_test.set_method("bm3")
    fitted_eos = best_fit()
    print('3rd order fit:')
    burnman.tools.pretty_print_values(fitted_eos.popt, fitted_eos.pcov, fitted_eos.fit_params)
    model_vs_3rd_order_correct = mg_perovskite_test.evaluate(['shear_wave_velocity'],
                                                             pressures, temperatures)[0]
    mg_perovskite_test.set_method("bm2")
    model_vs_3rd_order_incorrect = mg_perovskite_test.evaluate(['shear_wave_velocity'],
                                                               pressures, temperatures)[0]
    print('')


    plt.plot(pressures / 1.e9, model_vs_2nd_order_correct / 1000., color='r',
             linestyle='-', linewidth=2, label="Correct 2nd order fit")
    plt.plot(pressures / 1.e9, model_vs_2nd_order_incorrect / 1000., color='r',
             linestyle='-.', linewidth=2, label="Incorrect 2nd order fit")
    plt.plot(pressures / 1.e9, model_vs_3rd_order_correct / 1000., color='b',
             linestyle='-', linewidth=2, label="Correct 3rd order fit")
    plt.plot(pressures / 1.e9, model_vs_3rd_order_incorrect / 1000., color='b',
             linestyle='-.', linewidth=2, label="Incorrect 3rd order fit")
    plt.scatter(PTp_data[:,0] / 1.e9, PTp_data[:,2] / 1.e3)
    plt.ylim([6.55, 8])
    plt.xlim([25., 135.])
    plt.ylabel("Shear velocity (km/s)")
    plt.xlabel("Pressure (GPa)")
    plt.legend(loc="lower right", prop={'size': 12}, frameon=False)
    plt.savefig("output_figures/example_fit_data.png")
    plt.show()

    
