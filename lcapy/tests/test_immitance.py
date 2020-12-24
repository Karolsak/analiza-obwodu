from lcapy import *
import unittest
import sympy as sym

class LcapyTester(unittest.TestCase):

    """Unit tests for lcapy

    """

    def assertEqual2(self, ans1, ans2, comment):

        try:
            self.assertEqual(ans1, ans2, comment)
        except AssertionError as e:
            ans1.pprint()
            ans2.pprint()
            raise AssertionError(e)

    def test_impedance(self):

        ZC = C(3).Z

        self.assertEqual(ZC.Y(jw), 3 * jw, '.Y(jw)')
        self.assertEqual(ZC.Z(jw), -j / (3 * omega), '.Z(jw)')        
        self.assertEqual(ZC.R(jw), 0, '.R(jw)')
        self.assertEqual(ZC.G(jw), 0, '.G(jw)')
        self.assertEqual(ZC.X(jw), -1 / (3 * omega), '.X(jw)')
        self.assertEqual(ZC.B(jw), -3 * omega, '.B(jw)')

        ZR = R(3).Z

        self.assertEqual(ZR.Y(jw), expr('1 / 3'), '.Y(jw)')
        self.assertEqual(ZR.Z(jw), 3, '.Z(jw)')        
        self.assertEqual(ZR.R(jw), 3, '.R(jw)')
        self.assertEqual(ZR.G(jw), expr('1 / 3'), '.G(jw)')
        self.assertEqual(ZR.X(jw), 0, '.X(jw)')
        self.assertEqual(ZR.B(jw), 0, '.B(jw)')

        ZL = L(3).Z

        self.assertEqual(ZL.Y(jw), -j / (3 * omega), '.Y(jw)')
        self.assertEqual(ZL.Z(jw), 3 * jw, '.Z(jw)')        
        self.assertEqual(ZL.R(jw), 0, '.R(jw)')
        self.assertEqual(ZL.G(jw), 0, '.G(jw)')
        self.assertEqual(ZL.X(jw), 3 * omega, '.X(jw)')
        self.assertEqual(ZL.B(jw), 1 / (3 * omega), '.B(jw)')                

        Z1 = (R(2) + L(3)).Z

        self.assertEqual(Z1.Y(jw), 1 / (3 * jw + 2), '.Y(jw)')
        self.assertEqual(Z1.Z(jw), 3 * jw + 2, '.Z(jw)')        
        self.assertEqual(Z1.R(jw), 2, '.R(jw)')
        self.assertEqual(Z1.G(jw), 2 / (9 * omega**2 + 4), '.G(jw)')
        self.assertEqual(Z1.X(jw), 3 * omega, '.X(jw)')
        self.assertEqual(Z1.B(jw), 3 * omega / (9 * omega**2 + 4), '.B(jw)')

        Z1 = impedance(3 * s)
        Z2 = impedance(3 * jw)
        Z3 = impedance(6 * j * pi * f)
        self.assertEqual(Z1, Z2, 's-form and omega-form')
        self.assertEqual(Z1, Z3, 's-form and f-form')                
        
    def test_reciprocal(self):

        Z1 = impedance(2)
        Y1 = admittance(1 / 2)

        self.assertEqual(1 / Z1, Y1, '1 / Z')
        self.assertEqual(1 / Y1, Z1, '1 / Y')                
