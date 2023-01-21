#!/usr/bin/env python

from .missions import *

def download_dataset(mission, path, processing_lev, parameter, start_date, end_date, **kwargs):
    """ Initialise dataset and download product.
        
        Parameters
        ----------
        mission : str
          Mission name. Accepted values: ['sentinel-5p].
        path : str
          Output path.
        processing_lev : str
          Processing level of satellite product. Accepted values: ['L2', 'L3'].
        parameter : str
          Species name.
        start_date : str
          Start date for which the data will be read. Format: YYYY-MM-DD.
        end_date : str
          End date for which the data will be read. Format: YYYY-MM-DD.
    """
    
    if mission == 'sentinel-5p':
        explorer = Sentinel5p(mission=mission, path=path, processing_lev=processing_lev, 
                              parameter=parameter, start_date=start_date, end_date=end_date, 
                              **kwargs)

    else:
        msg = 'Data from {} cannot be retrieved using ebytes.'.format(mission)
        raise NotImplementedError(msg)

    explorer.download()

    return explorer
