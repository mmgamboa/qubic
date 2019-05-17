from __future__ import division
import sys
import time

import healpy as hp
import numpy as np

from pysm.nominal import models

import qubic

import ReadMC
import SpectroImLib as si

dictfilename = './spectroimaging.dict'

out_dir = './'#'/home/louisemousset/QUBIC/Qubic_work/SpectroImagerie/SimuLouise/repeat_ptg/'
name = 'repeat_pointing_01'

''' Parameters to be change for simulations:

[0] Sky creation:	d['nf_sub'] = 12 to 24 ? 4/5 diferent values?

[1] Pointing: 		d['random_pointing'] = True, 
					d['npointings'] = [1000,1500,2000]

[2] TOD creation: 	d['noiseless'] = [True, False]
					if False: change d['detector_nep'] only? 

[3] Reconstruction:	d['nf_sub_rec'] = [1,2,3,4,5,6,7,8] ? 
					tol = [5e-4, 1e-4, 5e-5, 1e-5, 5e-6] :o
					
'''
d = qubic.qubicdict.qubicDict()
d.read_from_file(dictfilename)

# Print dictionary and others parameters
# Save a file with all parameters
tem = sys.stdout
sys.stdout = f = open(out_dir + name + '.txt', 'wt')

print('Simulation Name: ' + name)
print('Dictionnary File: ' + dictfilename)
for k in d.keys():
    print(k, d[k])

sys.stdout = tem
f.close()

# ==========================================

t0 = time.time()

# ===== Sky Creation or Reading =====

sky_config = {
    'dust': models('d1', d['nside']),
    'cmb': models('c1', d['nside'])}

Qubic_sky = si.Qubic_sky(sky_config, d)
x0 = Qubic_sky.get_simple_sky_map()


# ==== Pointing strategy ====

p = qubic.get_pointing(d)

# ==== TOD making ====
TOD, maps_convolved = si.create_TOD(d, p, x0)

# ==== Reconstruction ====
for nf_sub_rec in d['nf_nrecon']:
    print(nf_sub_rec)
    print('-------------------------- Map-Making on {} sub-map(s)'.format(nf_sub_rec))
    maps_recon, cov, nus, nus_edge, maps_convolved = si.reconstruct_maps(TOD, d, p, nf_sub_rec, x0=x0)
    if nf_sub_rec == 1:
        maps_recon = np.reshape(maps_recon, np.shape(maps_convolved))
    # Look at the coverage of the sky
    cov = np.sum(cov, axis=0)
    maxcov = np.max(cov)
    unseen = cov < maxcov * 0.1
    maps_convolved[:, unseen, :] = hp.UNSEEN
    maps_recon[:, unseen, :] = hp.UNSEEN
    print('************************** Map-Making on {} sub-map(s)Done'.format(nf_sub_rec))

    ReadMC.save_simu_fits(maps_recon, cov, nus, nus_edge, maps_convolved,
                          out_dir, name, nf_sub_rec)

    t1 = time.time()
    print('************************** All Done in {} minutes'.format((t1 - t0) / 60))