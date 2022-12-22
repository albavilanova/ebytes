#!/usr/bin/env python

from .missions import *

def download_dataset(mission, path, processing_lev, parameter, input_type, 
                     start_date, end_date, lon_min, lon_max, lat_min, lat_max, 
                     **kwargs):
    """ Initialise dataset and download product. """

    if mission == 'sentinel-5p':
        explorer = Sentinel5p(mission=mission, path=path, processing_lev=processing_lev, 
                              parameter=parameter, input_type=input_type, start_date=start_date, end_date=end_date, 
                              lon_min=lon_min, lon_max=lon_max, lat_min=lat_min, lat_max=lat_max, **kwargs)

    else:
        msg = 'Data from {} cannot be retrieved using ebytes.'.format(mission)
        raise NotImplementedError(msg)

    explorer.download()

    return explorer