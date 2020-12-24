"""This module provides the Admittance class.  This is a generalized
impedance (s-domain) and converts to other representations.

Copyright 2019-2020 Michael Hayes, UCECE

"""
from __future__ import division
from .expr import expr
from .sexpr import LaplaceDomainExpression
from .units import u as uu

    
def admittance(arg, **assumptions):
    """Generic admittance factory function.

    Y(omega) = G(omega) + j * B(omega)

    where G is the conductance and B is the susceptance.

    Admittance is the reciprocal of impedance,

    Z(omega) = 1 / Y(omega)

    """    

    expr1 = expr(arg, **assumptions)
    if expr1.is_admittance:
        return expr1.apply_unit(1 / uu.ohms)

    if expr1.is_constant:
        expr1 = LaplaceDomainExpression(expr1)
    
    try:
        expr1 = expr1.as_admittance(expr1)
    except:
        raise ValueError('Cannot represent %s(%s) as admittance' % (expr1.__class__.__name__, expr1))        

    # Could use siemens but this causes comparison problems if
    # unit simplification not performed.
    return expr1.apply_unit(1 / uu.ohms)

