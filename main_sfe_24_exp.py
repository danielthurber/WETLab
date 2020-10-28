import os
import datetime
import shutil as sl
from create_boundary import create_boundary
from generate_file_structure import generate_file_structure
from copyfiles import copyfiles
from copyfiles import parameters

from update_attri_table import update_attri_table
from run_tuflow import run_tuflow
from run_tuflow import bc_data
from arcpy import env
from bankfull_stage_flow import stage_flow_inputs
from FloatToRaster import flt_to_tif
from distutils.dir_util import copy_tree
from bf_stage_flow_man import stage_flow_inputs_mannings
from trim_rasters import clip_rasters
from bf_stage_flow_man_exp import stage_flow_inputs_mannings_exp
from EHF_dist import distribution, flatten, get_max_dist, plot_distributions
from matplotlib import cm
import matplotlib.pyplot as plt
import matplotlib.colors as col
import pandas as pd

import numpy as np

os.chdir("F:/tuflow-wf_python3")
env.workspace = "F:/tuflow-wf_python3"

# Inputs:
n = 0.035  # Manning's n y

S = 0.0044  # slope
stages = np.array([0.05, 0.08, 0.1, 0.12, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.8, 1])  # proportions of bankfull depth to run
#stages = np.array([0.05])
Elevation = 999.1  # the bottom elevation (m)
avg_bed_el = 999.3
bf_wse =1000.7
NAME = 'sfe_24'  # file name of the ascii file

cell_size = "1"
# cell_size = "2"
grid_size = "310,50"
# end_time = [12, 6, 6, 6, 6, 6, 6]
end_time = 6
# copy GIS files to "\output_folder\sfe5_tuflow\Model

# Plot titles:
# SFE95 Surveyed Terrain
intitle = NAME + " Terrain"

# SFE95 RB Terrain - method 1
# intitle = "SFE95 RiverBuilder Terrain" #Base title to be added to the plot (specific plot information added later)


meter = '-2'  # buffer by x meters

# distribution parameters:
# single letter strings of parameters to create
# distributions for. options (case sensitive) are BSS, d, h, n, V
param_i = ['d', 'V']
param_name = ['depth', 'velocity']  # parameter names of distributions to plot
vel_samp_zoom = 500  # value to zoom y-axis to on velocity distributions
vel_prop_zoom = 0.005  # value to zoom y-axis to on velocity density distributions

# Code:
run_number = str(len(stages))  # how many discharge you want to run
create_boundary(NAME, meter)
generate_file_structure(NAME, run_number)
copyfiles(NAME, run_number)
stage_flow_inputs_mannings_exp(NAME, stages, S, n, Elevation, bf_wse)
#stage_flow_inputs_mannings(NAME, stages, S, n, Elevation,bf_wse)



parameters(NAME, run_number, cell_size, grid_size, end_time)
# update_attri_table(NAME)   # just copy the files in which the attributes are updated
# skip update_attri_table if you are using the updated files

run_tuflow(NAME, run_number)  # the results are stored in /results/grid/*.flt (raster files)
# bc_data.csv need to be placed in the input folder

copyloc = flt_to_tif(NAME, run_number, end_time)  # convert .flt files to .tif files

#copy main.py file into tuflow_runs/NAME/ folder
(pypath, pyfile) = os.path.split(__file__)
if os.path.exists(copyloc):
    sl.copyfile(__file__, copyloc + "/" + pyfile)

# Inputs:
# folder_name should be a string -directly- pointing to the folder that contains the depth_dist.xlsx and velocity_dist.xlsx files.
# Make sure it includes the / at the end. intitle is the base label to be added to the plot (and save
# file names in the communal location

folder_name = copyloc + "/results/hydraulic_performance/"
# dist_collection_fold is communal location of all distributions (should keep this the same for all runs)
dist_collection_fold = copyloc + "/../Distributions/"


no_tif = len(stages)    #number of stages to go through

max_bins = np.zeros_like(param_i, dtype='float')
for i in range(len(param_i)):
    max_bins[i] = get_max_dist(copyloc, param_i[i])
bin_sizes = max_bins / 100

plot_distributions(param_i, param_name, no_tif, folder_name, bin_sizes, max_bins, vel_samp_zoom, vel_prop_zoom, intitle,
                   dist_collection_fold)

print(datetime.datetime.now().strftime("%d-%B-%Y %I:%M %p"))
