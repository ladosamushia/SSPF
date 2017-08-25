# A code for testing SSPF.py
#
# Lado Samushia (colkhis@gmail.com) August, 2017.

import unittest

from astropy.io import fits
from astropy.table import Table

from SSPF import SampleSelect

from os import remove

catalogue = './test/test.fits'
random = './test/testran.fits'
ideal = './test/testid.fits'
output = './test/testout.fits'
selection = ['z_gt_0.3', 'type=ELG']

def remove_file(filename):
    try:
        remove(filename)
    except OSError:
        pass

class TestSSPF(unittest.TestCase):
    
    remove_file(output)
    SampleSelect(catalogue,random,ideal,output,selection)

    hdulist = fits.open(output)
    purity = hdulist[1].header['purity']
    completeness = hdulist[1].header['complete']
    
    def test_purity(self):
        self.assertEqual(self.purity,0.75)

    def test_completeness(self):
        self.assertEqual(self.completeness,0.5)

if __name__ == '__main__':
    unittest.main()
