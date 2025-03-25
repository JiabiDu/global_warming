#!/usr/bin/env python3
# shrink the data to degree resolution
import numpy as np
C=np.load('../../Labs/npz/sst_yearly_mean_1982_2023.npz')
sst=C['sst_yearly']
sst[sst==0]=np.nan
lon=C['lon']
lat=C['lat']

nlon=lon[2::4]
nlat=lat[2::4]

nsst=np.zeros([sst.shape[0],len(nlat),len(nlon)])
for ilon in range(len(nlon)):
    for ilat in range(len(nlat)):
        nsst[:,ilat,ilon]=np.nanmean(sst[:,ilat*4:(ilat+1)*4,ilon*4:(ilon+1)*4],axis=(1,2))
        
np.savez('../npz/sst_yearly_mean_1982_2023.npz',lon=nlon,lat=nlat,sst_year=nsst)