#!/usr/bin/env python

import os
import geojson
import pandas as pd
import numpy as np
import datetime as dt
import subprocess
from sentinelsat.sentinel import SentinelAPI, geojson_to_wkt
from .default_mission import Mission

class Sentinel5p(Mission):
   
   def __init__(self, mission='sentinel-5p', path=None, processing_lev=None, parameter=None, input_type=None, 
                start_date=None, end_date=None, lon_min=None,  lon_max=None, 
                lat_min=None, lat_max=None, **kwargs):

      super(Sentinel5p, self).__init__(mission=mission, path=path, processing_lev=processing_lev, 
                                       parameter=parameter, input_type=input_type, 
                                       start_date=start_date, end_date=end_date, 
                                       lon_min=lon_min, lon_max=lon_max, 
                                       lat_min=lat_min, lat_max=lat_max,
                                       **kwargs)
                                                               
      self.processing_lev = processing_lev
      self.input_type = input_type

      self.check_validity()

   def check_validity(self):
      """ Check if it is possible to download the data for a certain processing level and parameter. """

      if ((self.processing_lev == 'L3' and self.parameter not in ['NO2']) or
          (self.processing_lev == 'L2' and self.parameter not in ['NO2', 'O3', 'CO', 'SO2', 'HCHO'])):
         if self.parameter not in ['NO2']:
            msg = 'It is not possible to download {} {} data using ebytes.'.format(self.processing_lev,
                                                                                   self.parameter)
            raise NotImplementedError(msg)

      return None

   def search_period(self):
      """ Get range of dates for which the data will be downloaded. """

      range_dt = pd.date_range(np.datetime64(self.start_date), np.datetime64(self.end_date))
      
      if self.processing_lev == 'L3':
         dates = tuple(np.unique([date.strftime('%Y-%m') for date in range_dt]))
      
      elif self.processing_lev == 'L2':
         range_dt_initial = range_dt
         range_dt_final = range_dt_initial + dt.timedelta(hours = 23)
         dates = list(zip([date.strftime('%Y-%m-%dT%H:%M:%SZ') for date in range_dt_initial], 
                          [date.strftime('%Y-%m-%dT%H:%M:%SZ') for date in range_dt_final]))
      
      return dates

   def retrieve_product_type(self):
      """ Get product name as in S-5P Hub. """

      parameters = ['NO2', 'CO', 'O3', 'SO2', 'CH4', 'HCHO']
      product_types = ['L2__NO2___', 'L2__CO____', 'L2__O3____', 
                       'L2__SO2___', 'L2__CH4___', 'L2__HCHO__']

      rows = {'Nomenclature': parameters,
               'Product type': product_types
               }
      table = pd.DataFrame(rows)

      self.product_type = table['Product type'].loc[table['Nomenclature'] == self.parameter].iloc[0]

      return None

   def download(self):
      """ Query and download L2 data using Sentinel API (S-5P Hub) and L3 data from TEMIS. """

      # Get list of dates
      dates = self.search_period()

      if self.processing_lev == 'L2':

         # Initialize API
         user = 's5pguest' 
         password = 's5pguest' 
         api = SentinelAPI(user, password, 'https://s5phub.copernicus.eu/dhus/')

         # Create output directory if it does not exist
         os.makedirs(self.path, exist_ok=True)

         if self.input_type == 'manual':

            filename = input('Write file name: ')
            product_name = input('Write product name:')

            for date in dates:

               if os.path.isfile(filename_path):
                  print('The file exists, it will not be downloaded again.')

               else:
                  print('The file does not exist, it will be downloaded.')
                  print(f'Downloading {product_name}...')
                  filename_path = self.path + date[0].split('T')[0]
                  api.download(filename, directory_path = filename_path)

         elif self.input_type == 'query':

            self.retrieve_product_type()

            print('WARNING: The maximum number of items that can be shown is 10.')
            print('You can see all the results at https://s5phub.copernicus.eu/dhus/.')

            bbox = ((self.lon_min, self.lat_min), (self.lon_max, self.lat_max))
            poly = geojson.Polygon([[(bbox[0][0], bbox[0][1]), 
                                     (bbox[0][0], bbox[1][1]), 
                                     (bbox[1][0], bbox[1][1]), 
                                     (bbox[1][0], bbox[0][1]), 
                                     (bbox[0][0], bbox[0][1])]])

            for date in dates:

               products = api.query(area=geojson_to_wkt(poly),
                                    area_relation='Contains',
                                    producttype=self.product_type,
                                    processinglevel='L2',
                                    platformname='Sentinel-5 Precursor',
                                    instrumentname='TROPOspheric Monitoring Instrument',
                                    processingmode='Near real time',
                                    date=date,
                                    limit=10)

               items = list(products.items())
               
               if items:
                  for i in range(0, len(items)):
                        print('Number ', i, '-', items[i][1]['title'], sep = '')
            
               else: 
                  msg = 'There are no results for the processing mode NRT. '
                  msg += 'The search in the offline archives will start.'
                  print(msg)
                  products = api.query(area=geojson_to_wkt(poly),
                                       area_relation='Contains',
                                       producttype=self.product_type,
                                       processinglevel='L2',
                                       platformname='Sentinel-5 Precursor',
                                       instrumentname='TROPOspheric Monitoring Instrument',
                                       processingmode='Offline',
                                       date=date,
                                       limit=10)

                  items = list(products.items())

                  if items:
                     for i in range(0, len(items)):
                        print('Number ', i, '-', items[i][1]['title'], sep = '')
                  else: 
                     msg = 'There are no results in the offline archives. '
                     msg += 'The code will be interrupted.'
                     print(msg)
                     break
                     
               file_int = input('Select number or press Enter if you want to select the first result: ') or 0
               filename = items[int(file_int)][0]
               product_name = items[int(file_int)][1]['title'] + '.nc'

            print('SELECTED')
            print('File name:', filename)
            print('Product name:', product_name)
            
            filename_path = self.path + self.mission + '/' + self.processing_lev + '/' + self.parameter + '/' \
                             + date[0].split('T')[0]

            if os.path.isfile(filename_path + '/' + product_name):
               print('The file exists, it will not be downloaded again.')

            else:
               print('The file does not exist, it will be downloaded.')
               print(f'Downloading {product_name}...')
               api.download(filename, directory_path=filename_path)

         if not os.listdir(filename_path):
            os.rmdir(filename_path)
         else:
            print('Dataset was successfully downloaded!')

      elif self.processing_lev == 'L3':
         
         for date in dates:
            
            year = date.split('-')[0]
            month = date.split('-')[1]
            
            filename_path = self.path + '/' + self.mission + '/' + self.processing_lev + '/' + self.parameter + '/' \
                                    + year + '-'  + month
            os.makedirs(filename_path, exist_ok=True) 
            product_name = 'TROPOMI_L3_NO2_COLUMN_' + year + month + '.asc.gz'
            filename =filename_path + '/' + product_name

            path = ('https://d1qb6yzwaaq4he.cloudfront.net/tropomi/' \
                     + self.parameter.lower() + '/' + year \
                     + '/' + month + '/' + self.parameter.lower() + '_' + year + month + '.asc.gz')
            subprocess.run(['wget', '-q', '-nc', path, '-O', filename_path + '/' + product_name])
            print(filename)
            if os.stat(filename).st_size == 0:  
               os.remove(filename) 
               print(product_name, 'is not available.')

            else:
               print(product_name, 'was downloaded.')