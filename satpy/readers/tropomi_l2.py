# -*- coding: utf-8 -*-
# Copyright (c) 2018.
#
# Author(s):

#   Eysteinn Már Sigurðsson <eysteinn@vedur.is>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
""" OSI SAF ASCAT reader for Metop wind products as provided by KNMI
"""

from datetime import datetime

from satpy.readers.file_handlers import BaseFileHandler

from netCDF4 import Dataset as CDF4_Dataset

import xarray as xr
import dask.array as da
from satpy import CHUNK_SIZE
import numpy as np

class TROPOMIL2FileHandler(BaseFileHandler):

    def _read_nc_variables(self, ds):
        self.so2_tvc = ds['PRODUCT'].variables['sulfurdioxide_total_vertical_column'][0,:]

    def _read_data(self, filename):
        ds = CDF4_Dataset(filename, 'r')
        #self.filename_info['start_time'] = datetime.strptime(ds.getncattr('start_date') +
        #        ' ' + ds.getncattr('start_time'), '%Y-%m-%d %H:%M:%S')
        #self.filename_info['end_time'] = datetime.strptime(ds.getncattr('stop_date') +
        #        ' ' + ds.getncattr('stop_time'), '%Y-%m-%d %H:%M:%S')
        #self.filename_info['equator_crossing_time'] = datetime.strptime(ds.getncattr('equator_crossing_date') +
        #        ' ' + ds.getncattr('equator_crossing_time'), '%Y-%m-%d %H:%M:%S')
        #self.filename_info['orbit_number'] = str(ds.getncattr('orbit_number'))
        
        
        self.lats = ds['PRODUCT'].variables['latitude'][0,:]
        self.lons = ds['PRODUCT'].variables['longitude'][0,:]
        self._read_nc_variables(ds)
        ds.close()

    def __init__(self, filename, filename_info, filetype_info):
        super(TROPOMIL2FileHandler, self).__init__(filename, filename_info,
                                                      filetype_info)
        self.lons = None
        self.lats = None
        self.filename = filename
        self._read_data(filename)
        print('Init: '+ filename)

    def _get_vars(self, stdname, info):
        raise NotImplementedError()
        #if stdname in ['so2_total_column']:
        #    return xr.DataArray(da.from_array(self.so2_tvc, chunks=CHUNK_SIZE), name='abc',
        #                        attrs=info, dims=('y', 'x'))

    def get_dataset(self, key, info):
        stdname = info['standard_name']
        print('Reading: '+stdname+' from file: '+self.filename)
        if stdname in ['longitude', 'lon_so2', 'lon_aer_ai', 'lon_o3', 'lon_no2', 'lon_co']:
            print('Found lon')
            return xr.DataArray(self.lons, name=stdname,
                                attrs=info, dims=('y', 'x'))
        elif stdname in ['latitude', 'lat_so2', 'lat_aer_ai', 'lat_o3', 'lat_no2', 'lat_co']:
            print('Found lat')
            return xr.DataArray(self.lats, name=stdname,
                                attrs=info, dims=('y', 'x'))
        print('Not lat / long')
        return self._get_vars(stdname, info)

        # elif stdname in ['wind_direction']:
        #     return xr.DataArray(da.from_array(self.wind_direction, chunks=CHUNK_SIZE), name=key,
        #                         attrs=info, dims=('y', 'x'))

        # elif stdname in ['ice_prob']:
        #     return xr.DataArray(da.from_array(self.ice_prob, chunks=CHUNK_SIZE), name=key,
        #                         attrs=info, dims=('y', 'x'))

        # elif stdname in ['ice_age']:
        #     return xr.DataArray(da.from_array(self.ice_age, chunks=CHUNK_SIZE), name=key,
        #                         attrs=info, dims=('y', 'x'))



class TROPOMI_L2_SO2_FileHandler(TROPOMIL2FileHandler):
    def _read_nc_variables(self, ds):
        
        self.sulfurdioxide_total_vertical_column = ds['PRODUCT'].variables['sulfurdioxide_total_vertical_column'][0,:]
        self.qa_value = ds['PRODUCT']['qa_value'][0,:]
        #self.sulfurdioxide_total_vertical_column = np.ma.MaskedArray(self.sulfurdioxide_total_vertical_column, self.qa_value < 0.5)
        self.sulfurdioxide_total_vertical_column = np.ma.masked_where(self.qa_value < 0.5, self.sulfurdioxide_total_vertical_column)

        self.multiplication_factor_to_convert_to_DU = ds['PRODUCT'].variables['sulfurdioxide_total_vertical_column'].multiplication_factor_to_convert_to_DU

    def _get_vars(self, stdname, info):
        if stdname in ['sulfurdioxide_total_vertical_column']:
            return xr.DataArray(da.from_array(self.sulfurdioxide_total_vertical_column, chunks=CHUNK_SIZE), name=stdname,
                                attrs=info, dims=('y', 'x'))


class TROPOMI_L2_O3_FileHandler(TROPOMIL2FileHandler):
    def _read_nc_variables(self, ds):
        self.ozone_total_vertical_column = ds['PRODUCT'].variables['ozone_total_vertical_column'][0,:]

    def _get_vars(self, stdname, info):
        if stdname in ['ozone_total_vertical_column']:
            return xr.DataArray(da.from_array(self.ozone_total_vertical_column, chunks=CHUNK_SIZE), name=stdname,
                                attrs=info, dims=('y', 'x'))



class TROPOMI_L2_NO2_FileHandler(TROPOMIL2FileHandler):
    def _read_nc_variables(self, ds):
        self.nitrogendioxide_tropospheric_column = ds['PRODUCT'].variables['nitrogendioxide_tropospheric_column'][0,:]

    def _get_vars(self, stdname, info):
        if stdname in ['nitrogendioxide_tropospheric_column']:
            return xr.DataArray(da.from_array(self.nitrogendioxide_tropospheric_column, chunks=CHUNK_SIZE), name=stdname,
                                attrs=info, dims=('y', 'x'))


class TROPOMI_L2_NCHO_FileHandler(TROPOMIL2FileHandler):
    def _read_nc_variables(self, ds):
        self.formaldehyde_tropospheric_vertical_column = ds['PRODUCT'].variables['formaldehyde_tropospheric_vertical_column'][0,:]

    def _get_vars(self, stdname, info):
        if stdname in ['formaldehyde_tropospheric_vertical_column']:
            return xr.DataArray(da.from_array(self.formaldehyde_tropospheric_vertical_column, chunks=CHUNK_SIZE), name=stdname,
                                attrs=info, dims=('y', 'x'))


class TROPOMI_L2_AER_AI_FileHandler(TROPOMIL2FileHandler):
    def _read_nc_variables(self, ds):
        self.aerosol_index_340_380 = ds['PRODUCT'].variables['aerosol_index_340_380'][0,:]
        self.aerosol_index_354_388 = ds['PRODUCT'].variables['aerosol_index_354_388'][0,:]

    def _get_vars(self, stdname, info):
        if stdname in ['aerosol_index_340_380']:
            return xr.DataArray(da.from_array(self.aerosol_index_340_380, chunks=CHUNK_SIZE), name=stdname,
                                attrs=info, dims=('y', 'x'))
        if stdname in ['aerosol_index_354_388']:
            return xr.DataArray(da.from_array(self.aerosol_index_354_388, chunks=CHUNK_SIZE), name=stdname,
                                attrs=info, dims=('y', 'x'))




class TROPOMI_L2_CO_FileHandler(TROPOMIL2FileHandler):
    def _read_nc_variables(self, ds):
        self.qa_value = ds['PRODUCT']['qa_value'][0,:]
        self.carbonmonoxide_total_column = ds['PRODUCT'].variables['carbonmonoxide_total_column'][0,:]
        self.carbonmonoxide_total_column = np.ma.masked_where(self.qa_value < 0.5, self.carbonmonoxide_total_column)

        print('!!!!!!!!!!!!!!', self.carbonmonoxide_total_column.max())

    def _get_vars(self, stdname, info):
        if stdname in ['carbonmonoxide_total_column']:
            return xr.DataArray(da.from_array(self.carbonmonoxide_total_column, chunks=CHUNK_SIZE), name=stdname,
                                attrs=info, dims=('y', 'x'))

class TROPOMI_L2_CLOUD_FileHandler(TROPOMIL2FileHandler):
    def _read_nc_variables(self, ds):
        self.cloud_fraction = ds['PRODUCT'].variables['cloud_fraction'][0,:]

    def _get_vars(self, stdname, info):
        if stdname in ['cloud_fraction']:
            return xr.DataArray(da.from_array(self.cloud_fraction, chunks=CHUNK_SIZE), name=stdname,
                                attrs=info, dims=('y', 'x'))
