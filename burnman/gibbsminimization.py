# BurnMan - a lower mantle toolkit
# Copyright (C) 2012-2014, Myhill, R., Heister, T., Unterborn, C., Rose, I. and Cottaar, S.
# Released under GPL v2 or later.

import numpy as np
import scipy.linalg as linalg
import burnman
from burnman.processchemistry import *


def assemble_stoichiometric_matrix ( minerals):
    """
    This takes a list of minerals and assembles a matrix where 
    the rows are elements and the columns are species (or endmembers).
    If a solid solution is passed in, then the endmembers are extracted
    from it. 
    """
 
    elements = set()
    formulae = []

    # Make a list of the different formulae, as well as a set of 
    # the elements that we have present in the mineral list
    for m in minerals:
        # Add the endmembers if it is a solid solution
        if isinstance(m, burnman.SolidSolution):
            for e in m.base_material:
                f = e[0].params['formula']
                formulae.append(f)
                for k in f.keys():
                    elements.add(k)
        # Add formula if it is a simple mineral
        elif isinstance(m, burnman.Mineral):
            f = m.params['formula']
            formulae.append(f)
            for k in f.keys():
                elements.add(k)
        else:
            raise Exception('Unsupported mineral type, can only read burnman.Mineral or burnman.SolidSolution')

    #Listify the elements and sort them so they have a well-defined order.
    #This will be the ordering of the rows.  The ordering of the columns
    #will be the ordering of the endmembers as they are passed in.
    elements = list(elements)
    elements.sort()

    #Populate the stoichiometric matrix
    stoichiometric_matrix = np.empty( [ len(elements), len(formulae) ] )
    for i,e in enumerate(elements):
        for j,f in enumerate(formulae):
            stoichiometric_matrix[i,j] = ( f[e]  if e in f else 0.0 )

    return stoichiometric_matrix, elements, formulae


def compute_nullspace ( stoichiometric_matrix ):
    """
    Given a stoichiometric matrix, compute a basis for the nullspace.
    TODO: The basis for the nullspace is nonunique, and in general there
    is no reason to expect that the one returned by svd is in any way
    physically meaningful.  We would really like to have the 'sparsest'
    possible basis, which corresponds to the set of independent reactions
    with the fewest possible reactants.  Unfortunately this is an NP
    hard problem.  There are some ways to do it, but I have not gone for it.
    """

    eps = 1.e-10
    U, S, V = linalg.svd( stoichiometric_matrix)
    S=np.append(S, [0. for i in range(len(V)-len(S))])
    null_mask = (S <= eps)
    null_space = np.compress(null_mask, V, axis=0)
    return np.transpose(null_space)
    