'''
This script will read three input files: The catalogue, the random, and the
ideal files. It will subsample the catalogue based on the selection criteria
provided at the command line. It will also compute the completeness and the
purity of the subsample.

Arguments:
1 -- catalogue file name
2 -- random file name
3 -- ideal file name
4 -- output file name
5 and onwards -- optional selection criteria

Sample usage:
python sspf.py catalogue.fits random.fits ideal.fits subsample.fits z_gt_0.6 \
z_ls_0.7 type=ELG Haflux_gt_8e-16

Input: 
Three .fits files as described above. Random and ideal catalogues must have
matching unique object ID columns. 

Output:
One .fits file. Completeness and purity will be saved in the header. Selection
criteria will also be saved in the header. If the selection criteria have long
names they will be saved as 'hierarch' cards and astropy will issue a warning,
but I believe that's OK.

Notes:
If the selection criterion is not understood it will be ignored and a warning
will be issued.
Selection criteria must have one of either '_gt_', '_ls_', or '=' substrings in
them. _gt_ means greater, _ls_ means less, and = obviously means equal.
'''

from astropy.io import fits
from astropy.table import Table

from sys import argv
from sys import exit

from os.path import isfile

import numpy as np

catalogue = argv[1]
random = argv[2]
ideal = argv[3]
output = argv[4]
selection = argv[5:]

# Be careful not to overwrite existing files
if isfile(output):
    print('===============')
    print('file ' + output + ' exists. Delete it first')
    print('or change the output filename')
    print('===============')
    exit()

catalogue = Table.read(catalogue)
random = Table.read(random)
ideal = Table.read(ideal)

# Sub-select binary table based on selection criteria
for criterion in selection:
    print('Selecting by', criterion)
    if '_gt_' in criterion:
        column, value = criterion.split('_gt_')
        if column not in catalogue.colnames:
            print('WARNING: No column named', column, 'in the catalogue file')
            continue
        mask = (catalogue[column] < float(value))
        catalogue.remove_rows(mask)
    elif '_ls_' in criterion:
        column, value = criterion.split('_ls_')
        if column not in catalogue.colnames:
            print('WARNING: No column named', column, 'in the catalogue file')
            continue
        mask = (catalogue[column] > float(value))
        catalogue.remove_rows(mask)
    elif '=' in criterion:
        column, value = criterion.split('=')
        if column not in catalogue.colnames:
            print('WARNING: No column named', column, 'in the catalogue file')
            continue
        mask = (catalogue[column] != value)
        catalogue.remove_rows(mask)
    else:
        print('WARNING: Do not understand selection criterion', criterion)
    catalogue.meta[column+'_sel'] = criterion
Nsubcat = len(catalogue)
print(Nsubcat, 'objects were selected from the catalogue')

# Random
Nrandom = len(random)
rmask = np.ones(Nrandom)

for criterion in selection:
    if '_gt_' in criterion:
        column, value = criterion.split('_gt_')
        if column not in random.colnames:
            print('WARNING: No column named', column, 'in the random file')
            continue
        rmask = np.logical_and(rmask, random[column] > float(value))
    elif '_ls_' in criterion:
        column, value = criterion.split('_ls_')
        if column not in random.colnames:
            print('WARNING: No column named', column, 'in the random file')
            continue
        rmask = np.logical_and(rmask, random[column] < float(value))
    elif '=' in criterion:
        column, value = criterion.split('=')
        if column not in random.colnames:
            print('WARNING: No column named', column, 'in the random file')
            continue
        rmask = np.logical_and(rmask, random[column] != value)
    else:
        print('WARNING: Do not understand selection criterion', criterion)   

Nrand_selected = np.sum(rmask)
# IDs of selected objects
rand_selected = random['ID']
rand_selected = rand_selected[rmask]
print(Nrand_selected, 'objects were selected from the random file')

# Ideal 
Nideal = len(ideal)
imask = np.ones(Nideal)

for criterion in selection:
    if '_gt_' in criterion:
        column, value = criterion.split('_gt_')
        if column not in ideal.colnames:
            print('WARNING: No column named', column, 'in the ideal file')
            continue
        imask = np.logical_and(imask, ideal[column] > float(value))
    elif '_ls_' in criterion:
        column, value = criterion.split('_ls_')
        if column not in ideal.colnames:
            print('WARNING: No column named', column, 'in the ideal file')
            continue
        imask = np.logical_and(imask, ideal[column] < float(value))
    elif '=' in criterion:
        column, value = criterion.split('=')
        if column not in ideal.colnames:
            print('WARNING: No column named', column, 'in the ideal file')
            continue
        imask = np.logical_and(imask, ideal[column] != value)
    else:
        print('WARNING: Do not understand selection criterion', criterion)   

Nideal_selected = np.sum(imask)
# IDs of selected objects
ideal_selected = ideal['ID']
ideal_selected = ideal_selected[imask]
print(Nideal_selected, 'objects were selected from the ideal file')

# Number of objects that in selected random that are also in selected ideal
Nrand_ideal = len(set(rand_selected).intersection(ideal_selected))

# Compute completeness
completeness = Nrand_ideal/Nideal_selected
print('Completeness =', completeness)

# Purity
purity = Nrand_ideal/Nrand_selected
print('Purity =', purity)

# Save the subsample
catalogue.meta['purity'] = purity
catalogue.meta['complete'] = completeness
catalogue.write(output)
