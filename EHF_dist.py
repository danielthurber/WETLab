import shutil
from shutil import copyfile
# from os import sys, listdir, path
import sys, os

import rasterio
from rasterio.plot import show_hist
import matplotlib.pyplot as plt
import matplotlib.colors as col
from matplotlib import cm
import pandas as pd
import numpy as np

def flatten(x):
	list1 = []
	for sublist in x:
		for val in sublist:
			list1.append(val)
	return list1

def distribution(name,param,no_tif,folder_name,bsize,maxb):
	bins = np.arange(0,maxb,bsize)
	# colume names  of the depth; the numbers are related to the discharge
	flow_name = []
	for i in np.arange(1,no_tif+1,1):
			flow_name.append('d'+str(i))
	# create a dataframe to store _ distribution data
	df = pd.DataFrame({'bin':bins[:-1]})
	for k in np.arange(1,no_tif+1,1):
		file = 'T1_'+str(k)+'_'+ param + '_clip.tif'
		print(file)

		src = rasterio.open("{}/{}".format(folder_name,file))
		band = src.read(1)
		band0 = band.tolist()                 # transform array to list
		band1 = flatten(band0)                 # transform nested lists to one list
		band2 = [x for x in band1 if x > 0]  # remove negative values
		a = np.histogram(band2,bins)          # histogram with bin from 0 to 10 m for every 0.1 m
		y = a[0]                          # counts of the depth/velocity/BSS (0,0.1,10) meter
		# plt.plot(y)
		#plt.plot(band2)
		df[flow_name[k-1]] = y            # add the a column to dataframe
	bf_max = max(band2)
	filename = name + '_dist.xlsx'
	output_file = os.path.abspath(folder_name+filename)
#	output_file = name+'_dist.xlsx'
	# write to excel
	df.to_excel(output_file)
	return(bf_max)

def get_max_dist(path, pari):
	flowstagepath = path + '/flow_stage_depth.xlsx'
	flowstage = pd.read_excel(flowstagepath,index_col = 0)
	maxqind = flowstage.index[flowstage['Q (cms)']==max(flowstage['Q (cms)'])].get_values()[0]+1
	distpath = path + '/results/hydraulic_performance/T1_' +str(maxqind)+ '_' +pari+'_clip.tif'
	rastraw = rasterio.open(distpath).read(1).tolist()
	rastlst = flatten(rastraw)  # transform nested lists to one list
	rastpos = [x for x in rastlst if x > 0]  # remove negative values
	prop = 0.8
	maxparval = max(rastpos) * prop
	return(maxparval)

def plot_distributions(param_i,param_name,no_tif,folder_name,bin_sizes,max_bins,vel_samp_zoom,vel_prop_zoom,intitle,dist_collection_fold):
	cmap = cm.get_cmap("jet")  # specify colormap https://matplotlib.org/3.2.0/tutorials/colors/colormaps.html
	# The next two variables are for truncating the colormap. The value of each is a proportion of 1 where
	# the colormap should be truncated. For example mincmap = 0.2 and maxcmap = 0.8 would give a colormap that
	# is 20% to 80% of the original colormap. To invert, make the mincmap greater than the maxcmap.
	mincmap = 0
	maxcmap = 1

	bf_hydraulics = []
	if mincmap != 0 or maxcmap != 1:
		cmap = col.LinearSegmentedColormap.from_list(
			'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=mincmap, b=maxcmap),
			cmap(np.linspace(mincmap, maxcmap, 100)))

	# Create depth and velocity rasters and save to [parameter]_dist.xlsx
	for i in range(len(param_i)):
		bf_max = distribution(param_name[i], param_i[i], no_tif, folder_name, bin_sizes[i], max_bins[i])
		bf_hydraulics.append(bf_max)
		# filename = "%s_dist.xlsx" % (param_name[i])
		# output_dist = "/home/fengwei/FFF-connectors/files_output/Hydraulics_Distributions/%s" % (filename)
		# new_file_loc = os.path.abspath(folder_name + filename)
		# copyfile(output_dist,new_file_loc)
		distdf = pd.read_excel(folder_name + param_name[i] + "_dist.xlsx")
		allcols = list(distdf.columns)
		qcols = [k for k in allcols if k[0] == 'd']
		numsampdist = distdf.sum()

		qpropcols = []
		for j in range(len(qcols)):
			newcol = qcols[j] + 'prop'
			distdf[newcol] = distdf[qcols[j]] / numsampdist[qcols[j]]
			qpropcols.append(newcol)

		if param_i[i] == 'V':
			# fig = plt.figure()
			ax = distdf.plot(x="bin", y=qcols, title=intitle, cmap=cmap)
			ax.set_ylabel('Number of Samples')
			ax.set_xlabel(param_name[i])
			ax.set_ylim(0, vel_samp_zoom)
			ax.set_title(intitle + '\n Number of Samples - ' + param_name[i] + ' [Zoomed]')
			save_fig_title = 'Distribution ' + param_name[i] + ' Zoomed.png'
			plt.savefig(folder_name + save_fig_title)
			plt.savefig(dist_collection_fold + intitle + ' ' + save_fig_title)
			plt.show(block=False)

			# fig = plt.figure()
			ax = distdf.plot(x="bin", y=qpropcols, title=intitle, cmap=cmap)
			ax.set_ylabel('Proportion of Total Number of Samples')
			ax.set_xlabel(param_name[i])
			ax.set_ylim(0, vel_prop_zoom)
			ax.set_title(intitle + '\n Proportion of Total Number of Samples - ' + param_name[i] + ' [Zoomed]')
			save_fig_title = 'Distribution ' + param_name[i] + ' Prop Zoomed.png'
			plt.savefig(folder_name + save_fig_title)
			plt.savefig(dist_collection_fold + intitle + ' ' + save_fig_title)
			plt.show(block=False)

		ax = distdf.plot(x="bin", y=qcols, title=intitle, cmap=cmap)
		ax.set_ylabel('Number of Samples')
		ax.set_xlabel(param_name[i])
		ax.set_title(intitle + '\n Number of Samples - ' + param_name[i])
		save_fig_title = 'Distribution ' + param_name[i] + '.png'
		plt.savefig(folder_name + save_fig_title)
		plt.savefig(dist_collection_fold + intitle + ' ' + save_fig_title)
		plt.show(block=False)

		ax = distdf.plot(x="bin", y=qpropcols, title=intitle, cmap=cmap)
		ax.set_ylabel('Proportion of Total Number of Samples')
		ax.set_xlabel(param_name[i])
		ax.set_title(intitle + '\n Proportion of Total Number of Samples - ' + param_name[i])
		save_fig_title = 'Distribution ' + param_name[i] + ' Prop.png'
		plt.savefig(folder_name + save_fig_title)
		plt.savefig(dist_collection_fold + intitle + ' ' + save_fig_title)
		plt.show(block=False)

#
# #Inputs:
# #folder_name should be a string -directly- pointing to the folder that contains the depth_dist.xlsx and velocity_dist.xlsx files.
# #Make sure it includes the / at the end. intitle is the base label to be added to the plot (and save
# # file names in the communal location
#
# # SFE95 Surveyed Terrain
# intitle = "SFE95 Surveyed Terrain"
#
# # SFE95 RB Terrain - method 1
# # intitle = "SFE95 RiverBuilder Terrain" #Base title to be added to the plot (specific plot information added later)
#
# folder_name = "F:/tuflow_runs/SFE95_tuflow/results/hydraulic_performance/"
# #dist_collection_fold is communal location of all distributions (should keep this the same for all runs)
# dist_collection_fold = "F:/tuflow_runs/Distributions/"
#
# no_tif = 2
# param_i = ['d','V']
# param_name = ['depth', 'velocity']
#
# bin_sizes = [0.025,0.001]
# max_bins = [3.5,2]
#
# bf_hydraulics = []
#
# cmap = cm.get_cmap("jet") #specify colormap https://matplotlib.org/3.2.0/tutorials/colors/colormaps.html
# #The next two variables are for truncating the colormap. The value of each is a proportion of 1 where
# #the colormap should be truncated. For example mincmap = 0.2 and maxcmap = 0.8 would give a colormap that
# #is 20% to 80% of the original colormap. To invert, make the mincmap greater than the maxcmap.
# mincmap = 0
# maxcmap = 1
# vel_samp_zoom = 500
# vel_prop_zoom = 0.005
#
# if mincmap != 0 or maxcmap != 1:
#     cmap = col.LinearSegmentedColormap.from_list(
#         'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=mincmap, b=maxcmap),
#         cmap(np.linspace(mincmap, maxcmap, 100)))
#
# #Create depth and velocity rasters and save to [parameter]_dist.xlsx
# for i in range(len(param_i)):
# 	bf_max = distribution(param_name[i],param_i[i],no_tif,folder_name,bin_sizes[i],max_bins[i])
# 	bf_hydraulics.append(bf_max)
# 	# filename = "%s_dist.xlsx" % (param_name[i])
# 	# output_dist = "/home/fengwei/FFF-connectors/files_output/Hydraulics_Distributions/%s" % (filename)
# 	# new_file_loc = os.path.abspath(folder_name + filename)
# 	# copyfile(output_dist,new_file_loc)
# 	distdf = pd.read_excel(folder_name + param_name[i] +"_dist.xlsx")
# 	allcols = list(distdf.columns)
# 	qcols = [k for k in allcols if k[0]=='d']
# 	numsampdist = distdf.sum()
#
# 	qpropcols = []
# 	for i in range(len(qcols)):
# 		newcol = qcols[i] + 'prop'
# 		distdf[newcol] = distdf[qcols[i]] / numsampdist[qcols[i]]
# 		qpropcols.append(newcol)
#
#
# 	if param_i[i]=='V':
# 		# fig = plt.figure()
# 		ax = distdf.plot(x="bin",y=qcols,title=intitle,cmap=cmap)
# 		ax.set_ylabel('Number of Samples')
# 		ax.set_xlabel(param_name[i])
# 		ax.set_ylim(0,vel_samp_zoom)
# 		ax.set_title(intitle+'\n Number of Samples - ' +param_name[i]+ ' [Zoomed]')
# 		save_fig_title = 'Distribution ' +param_name[i]+ ' Zoomed.png'
# 		plt.savefig(folder_name + save_fig_title)
# 		plt.savefig(dist_collection_fold + intitle + ' ' + save_fig_title)
# 		plt.show(block=False)
#
# 		# fig = plt.figure()
# 		ax = distdf.plot(x="bin", y=qpropcols, title=intitle, cmap=cmap)
# 		ax.set_ylabel('Proportion of Total Number of Samples')
# 		ax.set_xlabel(param_name[i])
# 		ax.set_ylim(0, vel_prop_zoom)
# 		ax.set_title(intitle + '\n Proportion of Total Number of Samples - ' +param_name[i]+ ' [Zoomed]')
# 		save_fig_title = 'Distribution ' +param_name[i]+ ' Prop Zoomed.png'
# 		plt.savefig(folder_name + save_fig_title)
# 		plt.savefig(dist_collection_fold + intitle + ' ' + save_fig_title)
# 		plt.show(block=False)
#
# 	ax = distdf.plot(x="bin",y=qcols,title=intitle,cmap=cmap)
# 	ax.set_ylabel('Number of Samples')
# 	ax.set_xlabel(param_name[i])
# 	ax.set_title(intitle+'\n Number of Samples - ' +param_name[i])
# 	save_fig_title = 'Distribution '+param_name[i]+'.png'
# 	plt.savefig(folder_name + save_fig_title)
# 	plt.savefig(dist_collection_fold + intitle + ' ' + save_fig_title)
# 	plt.show(block=False)
#
# 	ax = distdf.plot(x="bin",y=qpropcols,title=intitle,cmap=cmap)
# 	ax.set_ylabel('Proportion of Total Number of Samples')
# 	ax.set_xlabel(param_name[i])
# 	ax.set_title(intitle+'\n Proportion of Total Number of Samples - ' +param_name[i])
# 	save_fig_title = 'Distribution ' +param_name[i]+ ' Prop.png'
# 	plt.savefig(folder_name + save_fig_title)
# 	plt.savefig(dist_collection_fold + intitle + ' ' + save_fig_title)
# 	plt.show(block=False)
#

