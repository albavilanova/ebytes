#!/usr/bin/env python

class Mission(object):

    def __init__(self, path=None, parameter=None, start_date=None, 
                 end_date=None, lon_min=None, lon_max=None, lat_min=None, 
                 lat_max=None, **kwargs):
      
        self.path = path
        self.parameter = parameter
        self.start_date = start_date
        self.end_date = end_date
        self.lon_min = lon_min
        self.lon_max = lon_max
        self.lat_min = lat_min
        self.lat_max = lat_max
    
    def download(self):

        return None