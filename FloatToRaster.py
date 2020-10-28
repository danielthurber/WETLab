# Name: FloatToRaster_Ex_02.py
# Description: Converts a file of binary floating-point values representing 
#    raster data to a raster dataset.

# Import system modules
import os, sys
import arcpy
import shutil
from distutils.dir_util import copy_tree
from datetime import datetime as dt
from trim_rasters import clip_rasters
arcpy.env.workspace = "F:/tuflow_runs"
arcpy.env.overwriteOutput = True
os.chdir("F:/tuflow_runs")

def flt_to_tif(NAME,run_number,end_time):  # NAME: "location_channel type, e.g. T5_1
    
    # establish end_time as a list of times for each run
    if isinstance(end_time,int):
        end_time_num = [end_time]*int(run_number)
        end_time = [str(x) for x in end_time_num]
    if isinstance(end_time,list):
        if len(end_time) != int(run_number):
            raise Exception('The number of values provided in end_time is not equal to the number of stages provided. Check this and run again.')
        else:
            end_time = [str(x) for x in end_time]    

    mapOutputInterval = "600"
    map_time_step_min = int(mapOutputInterval)/60

    run_number = int(run_number)
    result_path = os.path.abspath("output_folder/" + NAME + "_tuflow/results/"
                  +"/hydraulic_performance")
    
    for i in range(run_number):                 # for each run
        os.chdir("F:/tuflow-wf_python3")
        run = "{0:0=3d}".format(i+1)            # index of the run

## Create a "hydraulic performance" folder in each run folder
        tif_path = os.path.abspath("output_folder/" + NAME + "_tuflow/results/"
                       + run +"/hydraulic_performance")
        try:
            os.mkdir(tif_path)              
        except FileExistsError:
            print('Directory not created.')
        end_time_i = int(end_time[i])

#BSS: shear stress, d: depth, h: water level, n: Manning's n           
        for h in {'_BSS_', '_d_', '_h_', '_n_', '_V_'}:    
## create the path variable of the .flt files
            os.chdir("F:/tuflow-wf_python3")
            flt_path = os.path.abspath("output_folder/" + NAME + "_tuflow/results/"
                                       + run +"/grids/")
## calculate the number of maps created each hour
            maps_no_hr = int(60/map_time_step_min)
            for j in range(int(end_time_i)):         # each hour
                hr = "{0:0=3d}".format(j)
                for k in range(maps_no_hr):        # within each hour
## create filename variable for the .flt and .tif
                    minute = "{0:0=2d}".format(int(k*map_time_step_min))                
                    flt_name = NAME + h + hr + '_' + minute + '.flt'
                    print(flt_name)
                    input_name = os.path.abspath(flt_path +"/" + flt_name)
                    tif_name = 'T1' + h + hr + '_' + minute + '.tif'
                    output_name = os.path.abspath(flt_path + "/" + tif_name)
# Execute FloatToRaster
                    try:
                        arcpy.FloatToRaster_conversion(input_name, output_name)
                    except arcpy.ExecuteError:
                        print(arcpy.GetMessages())
                      
#                    arcpy.FloatToRaster_conversion(input_name, output_name)
## create the filename variable for the last map and convert it to .tif
#            flt_name = NAME + h + "{0:0=3d}".format(end_time) + '_' + '00' + '.flt'
#            print(flt_name)
#            input_name = os.path.abspath(flt_path +"/" + flt_name)
#            tif_name = NAME + h + "{0:0=3d}".format(end_time) + '_' + '00' + '.tif'
#            output_name = os.path.abspath(flt_path + "/" + tif_name)  
            
#            try:
#                arcpy.FloatToRaster_conversion(input_name, output_name)
#            except arcpy.ExecuteError:
#                print(arcpy.GetMessages())            

## copy the last .tif to the "hydraulic performacne" folder
            h_p_name = os.path.abspath(result_path +"/" + 'T1' + '_' + str(i+1) + h + '.tif')
            try:
                shutil.copy(output_name, h_p_name)

            except FileNotFoundError:
                if not os.path.exists(result_path):
                    os.mkdir(result_path)
                shutil.copy(output_name, h_p_name)
#                print('Directory not created.')            
    outfold = os.path.abspath("F:/tuflow_runs/" + NAME + "_tuflow")

    clip_rasters(NAME) #clips .tif outputs to remove runway, deletes all files that are not .tif

    #if no tuflow_runs folder exists, create one.  If it does exist, create new folder with timestamp
    if not os.path.exists(outfold):
        thirdloc = outfold
    else:
        now = dt.now()
        nowstr = now.strftime("%Y%m%d-%H%M%S")
        thirdloc = outfold + "_" + nowstr
    try:
        os.mkdir(thirdloc) #thirdloc is new destination folder

        startfold = os.path.abspath("output_folder/" + NAME + "_tuflow")
        foldsize = sum(os.path.getsize(os.path.join(dirpath, filename)) for dirpath, dirnames, filenames in os.walk(startfold) for
            filename in filenames)/1073741824
        print('Copying ' +str(round(foldsize,2))+ ' GB of TUFLOW results to external location')
        copy_tree(os.path.abspath(startfold),thirdloc)
    except:
        print('Copy failed, make sure to copy folder from output_folder to a safe place')
        thirdloc = startfold
    return thirdloc
