"""This module provides the Impedance class.  This is a generalized
impedance (s-domain) and converts to other representations.

Copyright 2019--2020 Michael Hayes, UCECE

"""
from __future__ import division
from .expr import expr
from .sexpr import LaplaceDomainExpression
from .units import u as uu


def impedance(arg, **assumptions):
    """Generic impedance factory function.

    Y(omega) = G(omega) + j * B(omega)

    where G is the conductance and B is the susceptance.

    Admittance is the reciprocal of impedance,

    Z(omega) = 1 / Y(omega)

    """        

    expr1 = expr(arg, **assumptions)
    if expr1.is_impedance:
        return expr1.apply_unit(uu.ohms)            

    if expr1.is_constant:
        expr1 = LaplaceDomainExpression(expr1)
    
    try:
        expr1 = expr1.as_impedance(expr1)
    except:    
        raise ValueError('Cannot represent %s(%s) as impedance' % (expr1.__class__.__name__, expr1))
        
    return expr1.apply_unit(uu.ohms)    
    
