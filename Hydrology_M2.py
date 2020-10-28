import os
import pandas as pd
from geopandas import GeoSeries, GeoDataFrame, read_file, gpd
from osgeo import gdal, ogr, osr
import rasterio as rio
from rasterstats import zonal_stats
from pylab import *
from matplotlib import pyplot as plt
import matplotlib
from matplotlib import colors
%matplotlib inline
