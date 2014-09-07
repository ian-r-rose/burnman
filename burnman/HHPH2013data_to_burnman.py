# BurnMan - a lower mantle toolkit
# Copyright (C) 2012-2014, Myhill, R., Heister, T., Unterborn, C., Rose, I. and Cottaar, S.
# Released under GPL v2 or later.

# This is a standalone program that converts a tabulated version of the Stixrude and Lithgow-Bertelloni data format into the standard burnman format (printed to stdout)


import sys


def read_dataset(datafile):
    f=open(datafile,'r')
    ds=[]
    for line in f:
        ds.append(line.decode('utf-8').split())
    return ds

ds=read_dataset('HHPH2013_endmembers.dat')

print 'from burnman.mineral import Mineral'
print 'from burnman.processchemistry import read_masses, dictionarize_formula, formula_mass'
print ''
print 'atomic_masses=read_masses()'
print ''

param_scales = [  -1., -1., #not nubmers, so we won't scale
                  1.e3, 1.e3, #kJ -> J
                  1.0, # J/K/mol
                  1.e-5, # kJ/kbar/mol -> m^3/mol
                  1.e3, 1.e-2, 1.e3, 1.e3, # kJ -> J and table conversion for b
                  1.e-5, # table conversion
                  1.e8, # kbar -> Pa
                  1.0, # no scale for K'0
                  1.e-8] #GPa -> Pa # no scale for eta_s 
           

formula='0'
for idx, m in enumerate(ds):
    if idx == 0:
        param_names=m
    else:   
        print 'class', m[0].lower(), '(Mineral):'
        print '    def __init__(self):'
        print ''.join(['       formula=\'',m[1],'\''])
        print '       formula = dictionarize_formula(formula)'
        print '       self.params = {'
        print ''.join(['            \'name\': \'', m[0], '\','])
        print '            \'formula\': formula,'
        print '            \'equation_of_state\': \'mtait\','
        for pid, param in enumerate(m):
            if pid > 1 and pid != 3 and pid<6:
                print '            \''+param_names[pid]+'\':', float(param)*param_scales[pid], ','

        print '            \'Cp\':', [round(float(m[i])*param_scales[i],10) for i in [6, 7, 8, 9]], ','
        for pid, param in enumerate(m):
            if pid > 9:
                print '            \''+param_names[pid]+'\':', float(param)*param_scales[pid], ','



        print '            \'n\': sum(formula.values()),'
        print '            \'molar_mass\': formula_mass(formula, atomic_masses)}'
        print ''
        print '       self.uncertainties = {'
        print '            \''+param_names[3]+'\':', float(m[3])*param_scales[3], '}'
        print ''
