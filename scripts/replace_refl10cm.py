#!/usr/bin/env python3
"""Replace refl10cm in analysis file with values from 1-step MPAS output."""
import sys
import netCDF4 as nc

if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} MPASOUT_FILE ANA_FILE", file=sys.stderr)
    sys.exit(1)

mpasout_file, ana_file = sys.argv[1], sys.argv[2]

ds_src = nc.Dataset(mpasout_file, 'r')
ds_dst = nc.Dataset(ana_file, 'r+')

ds_dst.variables['refl10cm'][0, :, :] = ds_src.variables['refl10cm'][0, :, :]
if 'refl10cm_max' in ds_src.variables and 'refl10cm_max' in ds_dst.variables:
    ds_dst.variables['refl10cm_max'][0, :] = ds_src.variables['refl10cm_max'][0, :]

ds_src.close()
ds_dst.close()
