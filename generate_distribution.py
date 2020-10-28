import numpy as np
from EHF_dist import distribution, flatten, get_max_dist,plot_distributions

param_i = ['d','V']
param_name = ['depth', 'velocity'] #parameter names of distributions to plot
vel_samp_zoom = 500 #value to zoom y-axis to on velocity distributions
vel_prop_zoom = 0.005 #value to zoom y-axis to on velocity density distributions
copyloc = "F:/tuflow_runs/SFE95_tuflow" # edit me
intitle = "SFE95 Surveyed Terrain"
no_tif = 2 # number of flows to get distributions for


folder_name = copyloc +"/results/hydraulic_performance/"
#dist_collection_fold is communal location of all distributions (should keep this the same for all runs)
dist_collection_fold = copyloc + "/../Distributions/"
max_bins = np.zeros_like(param_i,dtype='float')
for i in range(len(param_i)):
    max_bins[i] = get_max_dist(copyloc,param_i[i])
bin_sizes = max_bins/100


plot_distributions(param_i,param_name,no_tif,folder_name,bin_sizes,max_bins,vel_samp_zoom,vel_prop_zoom,intitle,dist_collection_fold)