import arcpy
from arcpy import env
import os
from shutil import copyfile, copytree

def clip_rasters(NAME):
    #designate folder and .asc file paths
    hyd_perf_folder = os.path.abspath("output_folder/" + NAME + "_tuflow/results/hydraulic_performance/")

    #asc_file_path = os.path.abspath("input_folder/" + NAME + ".asc")

    clip_extent = os.path.abspath("output_folder/" + NAME + "_tuflow/model/gis/2d_trim_" + NAME + "_R.shp")

    #create list of all files in hydraulic performance folder
    old_rasters = os.listdir(hyd_perf_folder)

    for name in old_rasters:
        try:
            tif_name = name.replace('.tif','')

         # copy .prj file into hydraulic performance folder and assign to given tif
            #prj_file_path = os.path.abspath("input_folder/" + NAME + ".prj")
            #copyfile(prj_file_path, hyd_perf_folder + '/' + tif_name + '.prj')

            #create new raster as a clipped version of the original
            in_raster = hyd_perf_folder + '\\' + tif_name + '.tif'
            out_raster = hyd_perf_folder + '\\' + tif_name + 'clip.tif'
            arcpy.Clip_management(in_raster, '#', out_raster, clip_extent, '0', 'ClippingGeometry', 'NO_MAINTAIN_EXTENT')
            if os.path.isfile(out_raster):
                print ('clipped ' + tif_name + ' to ' + tif_name + 'clip.tif')
                os.remove(in_raster)
            else:
                print ('failed to clip ' + in_raster)
                continue
        except:
            print (name + ' does not exist')
    #loop through all files in hydraulic_performance, delete anything that is not a .tif
    allfiles = os.listdir(hyd_perf_folder)

    for i in allfiles:
        if not (i[-4:] == '.tif'):
            os.remove(hyd_perf_folder + '\\' + i)
        else:
            continue

def delete_excess(NAME):
    hyd_perf_folder = os.path.abspath("output_folder/" + NAME + "_tuflow/results/hydraulic_performance/")
    allfiles = os.listdir(hyd_perf_folder)

    for i in allfiles:
        if not (i[-4:] == '.tif'):
            os.remove(hyd_perf_folder + '\\' + i)
        else:
            continue