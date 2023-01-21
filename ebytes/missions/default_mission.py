#!/usr/bin/env python

import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import cartopy.feature as cfeature
import matplotlib.cm as cm
from matplotlib import pyplot as plt


class Mission(object):

    def __init__(self, mission=None, path=None, processing_lev=None, parameter=None, 
                 start_date=None, end_date=None, **kwargs):

        self.mission = mission
        self.path = path
        self.parameter = parameter
        self.start_date = start_date
        self.end_date = end_date
        self.processing_lev = processing_lev
    
    def download(self):

        return None

    def read(self):

        return None
        
    def visualize(self, data_array, latitude_array, longitude_array, units, fig_title, 
                  color_scale='viridis', fig_size=(20, 10), projection=ccrs.PlateCarree(), vmin=None, vmax=None, 
                  extent=None, set_global=False):
        """ Visualize product in map given the data and projection. 
            Reference: https://gitlab.eumetsat.int/eumetlab/atmosphere/atmosphere/-/blob/master/functions.ipynb#visualize_pcolormesh.
          
            Parameters
            ----------
            data_array : xarray.DataArray
              Parameter data in object. It must be 2D.
            latitude_array : xarray.DataArray
              Latitude data in object. It must be 2D.
            longitude_array : xarray.DataArray
              Longitude data in object. It must be 2D.
            units : str
              Parameter units.
            fig_title : str
              Map title.
            color_scale : str
              Color scale in map.
            projection : cartopy.crs
              Map projection.
            vmin : float
              Minimum value of parameter data to show on map.
            vmax : float
              Maximum value of parameter data to show on map.
            extent : list
              Map extent as in [lonmin, lonmax, latmin, latmax].
          
        """

        fig = plt.figure(figsize=fig_size)
        ax = plt.axes(projection=projection)
        img = plt.pcolormesh(longitude_array, latitude_array, data_array, 
                            cmap=plt.get_cmap(color_scale), transform=ccrs.PlateCarree(),
                            vmin=vmin,
                            vmax=vmax,
                            shading='auto')

        ax.add_feature(cfeature.BORDERS, edgecolor='black', linewidth=1)
        ax.add_feature(cfeature.COASTLINE, edgecolor='black', linewidth=1)

        if (projection==ccrs.PlateCarree()):
            if extent is not None:
                ax.set_extent(extent, projection)
            gl = ax.gridlines(draw_labels=True, linestyle='--')
            gl.top_labels=False
            gl.right_labels=False
            gl.xformatter=LONGITUDE_FORMATTER
            gl.yformatter=LATITUDE_FORMATTER
            gl.xlabel_style={'size':14}
            gl.ylabel_style={'size':14}
        
        if set_global:
            ax.set_global()
            ax.gridlines()

        cbar = fig.colorbar(img, ax=ax, orientation='horizontal', fraction=0.05, pad=0.1)
        cbar.set_label(units, fontsize=16)
        cbar.ax.tick_params(labelsize=14)
        ax.set_title(fig_title, fontsize=20, pad=20.0)
