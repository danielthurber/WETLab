# -*- coding: utf-8 -*-
"""
Created on Mon Mar  4 18:41:18 2019

@author: Fengwei
"""
import os
#import errno
#import subprocess
from shutil import rmtree, copyfile, copy2, copytree, copy
import csv


def copyfiles(NAME, run_number):
    

#    output_folder = os.path.abspath("output_folder/" + NAME + "_tuflow/")
#    bc_dbase_folder_init = os.path.abspath(
#        "output_folder/" + NAME + "_tuflow/bc_dbase/init")
#    bc_dbase_folder = os.path.abspath(
#        "output_folder/" + NAME + "_tuflow/bc_dbase/")
    model_folder = os.path.abspath("output_folder/" + NAME + "_tuflow/model/")
#    runs_folder_init = os.path.abspath("output_folder/" + NAME + "_tuflow/runs/init/")
    runs_folder = os.path.abspath("output_folder/" + NAME + "_tuflow/runs/")
#    check_folder_init = os.path.abspath("output_folder/" + NAME + "_tuflow/check/init/")
#    results_folder_init = os.path.abspath("output_folder/" + NAME + "_tuflow/results/init/")
#    check_folder = os.path.abspath("output_folder/" + NAME + "_tuflow/check/")
#    results_folder = os.path.abspath("output_folder/" + NAME + "_tuflow/results/")
#    grid_folder = os.path.abspath("output_folder/" + NAME + "_tuflow/model/grid/") 
    
    desired_files = ["2d_code_empty_R", "2d_loc_empty_L",
                     "2d_mat_empty_R", "2d_po_empty_L", "2d_po_empty_P"]
    empty_folder = os.path.abspath("output_folder/" + NAME + "_tuflow/model/gis/empty")
    empty_files = os.listdir(empty_folder)
    print(empty_files)
    
    for f in empty_files:
        file_path = os.path.join(model_folder + "\\gis\\empty", f)
        print(f)

        if f.split(".")[0] == '2d_sa_empty_R':
            des_path = os.path.join(
                model_folder + "\\gis", f.replace("_empty_", "_"+NAME+"_QT_"))
            print(des_path)
        elif f.split(".")[0] == '2d_bc_empty_L':
            des_path = os.path.join(
                model_folder + "\\gis", f.replace("_empty_", "_"+NAME+"_HT_"))
        elif f.split(".")[0] in desired_files:
            des_path = os.path.join(
                model_folder + "\\gis", f.replace("_empty_", "_"+NAME+"_"))
        else:
            continue

        copyfile(file_path, des_path)
    gis_transfer = input("Automatically copy gis folder from gis files to output folder? (y/n)")
    if gis_transfer == 'n':
        input ("Manually copy completed shapefiles to /model/gis folder. When complete, press enter to continue..." )
    else:
        full_folder = os.path.abspath('F:/tuflow-wf_python3/gis files/' + NAME + '/gis')
        empty_gis_folder = os.path.abspath('F:/tuflow-wf_python3/output_folder/' + NAME + '_tuflow/model/gis')
        try:
            rmtree(empty_gis_folder)
        except:
            print('Empty folder was not found')

        try:
            copytree(full_folder,empty_gis_folder)
        except:
            print('Failed to copy folder from gis files to output_folder')
            input("Manually copy completed shapefiles to /model/gis folder. When complete, press enter to continue...")


def parameters(NAME, run_number, cell_size, grid_size,end_time):
#    iwl = input("Downstream water surface elevation [m] (e.g. 1003.432) -> ") or "1003.432"
#
#    print("")
#    print("Values inside the parenthesis are default values. Hit enter to accept default value or update with new value by typing in value and hitting enter.")
#    cell_depth = input("Cell Wet/Dry Depth(0.1 m) -> ") or "0.1"
#    end_time = input("End Time(2 hrs) -> ") or "2"
#    timestep = input("Time Step(2.5 s) NOTE: use timestep that is 1/4 of grid size in meters -> ") or "2.5"
#    mapOutput = input("Start Map Output(0 s) -> ") or "0"
#    mapOutputInterval = input("Map Output Interval(600 s) -> ") or "600"
#    tsOutputInterval = input(
#        "Time Series Output Interval(60 s)  -> ") or "60"
#    cell_depth = '0.1'
    if isinstance(end_time,int):
        end_time_num = [end_time]*int(run_number)
        end_time = [str(x) for x in end_time_num]
    if isinstance(end_time,list):
        if len(end_time) != int(run_number):
            raise Exception('The number of values provided in end_time is not equal to the number of stages provided. Check this and run again.')
        else:
            end_time = [str(x) for x in end_time]
        
    timestep = str(float(cell_size)/4) # time step must be 1/4 of cell size
    mapOutput = "0"
    mapOutputInterval = "600"
    tsOutputInterval = "60"

    model_folder = os.path.abspath("output_folder/" + NAME + "_tuflow/model/")
#    runs_folder_init = os.path.abspath("output_folder/" + NAME + "_tuflow/runs/init/")
    runs_folder = os.path.abspath("output_folder/" + NAME + "_tuflow/runs/")
    
    
    filename =NAME+'_bc_data.csv'
    iwl_list = []
    with open(os.path.join("input_folder" + "/" + filename), 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
             iwl_list.append(row['RPout'])
             
            
    for i in range(int(run_number)):
         
        iwl = iwl_list[i]       
        current_run =  "{0:0=3d}".format(i+1)
        f = open(os.path.join(runs_folder + "\\" +current_run, NAME + ".tcf"), "a")
        # f.write("\nDemo Model == ON\n" +
        f.write("\n" +
                # "\nUnits == US Customary" +
                "\nGeometry Control File  ==  ..\\..\\model\\" + NAME + ".tgc" +
                "\nBC Control File == ..\\..\\model\\" + NAME + ".tbc" +
                "\nBC Database == ..\\..\\bc_dbase\\" + current_run +"\\2d_bc_" + NAME + ".csv" +
                "\nRead Materials File == ..\\..\\model\\materials.csv" + "     ! This provides the link between the material ID defined in the .tgc and the Manning's roughess" +
                "\nRead GIS PO == ..\\..\\model\\gis\\2d_po_" + NAME + "_P.shp" + "     ! velocity monitoring point locations" +
                "\nRead GIS PO == ..\\..\\model\\gis\\2d_po_" + NAME + "_L.shp" + "     ! flow monitoring xs lines" +
                "\nSolution Scheme == HPC  !This command specifies that you want to run TUFLOW using the HPC solution scheme or engine." +
                "\nHardware == GPU  !CPU is default. The hardware command instructs TUFLOW HPC to run using GPU hardware. This is typically orders of magnitude faster than on CPU." +
                "\n"+
                "\nViscosity Formulation == SMAGORINSKY" +
                "\nViscosity Coefficients == 0.5, 0.005" +
                "\nSET IWL == " + iwl + "   ! matches the downstream WSE" +
                #"\nCell Wet/Dry Depth == " + cell_depth + "     ! Forces cells to be dry if their depth is < 0.1 m" +
                "\n" +
                "\nStart Time == 0" + "     ! Start Simulation at 0 hours" +
                "\nEnd Time == " + end_time[i] + "     ! End Simulation (hrs)" +
                "\nTimestep == " + timestep + "     ! Use a 2D time step that is ~1/4 of the grid size in m (10 m * 0.25 -> 2.5 s)" +
                "\n" +
                "\nLog Folder == Log" + "   ! Redirects log output (eg. .tlf and _messages GIS layers to the folder log" +
                "\nOutput Folder == ..\\..\\results\\" + current_run + "\\" + "     ! Redirects results files to TUFLOW\Results\RUN" +
                "\nWrite Check Files == ..\\..\\check\\" + current_run + "\\" + "   ! Specifies check files to be written to TUFLOW\check\RUN" +
                "\nMap Output Format == GRID XMDF" + "  ! Output directly to GIS (grid) as well as SMS (xmdf compact) format" +
                "\nMap Output Data Types == h d n V BSS" + "    ! wse depth Manning's n velocity bed shear stress" +
                "\nStart Map Output == " + mapOutput + "    ! Start map output at 0 hours" +
                "\nMap Output Interval == " + mapOutputInterval + "     ! Output every 600 seconds (10 minutes)" +
                "\nGRID Map Output Data Types == h d n V BSS" +
                "\nTime Series Output Interval  == " + tsOutputInterval + "     ! time interval of output in seconds"
                )

    # Steps 5.1, 5.2
    with open(os.path.join(model_folder, NAME + ".tbc"), 'r+') as myfile:
        text = myfile.read().replace("NAME", NAME)
        myfile.seek(0)
        myfile.write(text)
        myfile.truncate()

    with open(os.path.join(model_folder, NAME + ".tgc"), 'r+') as myfile:

#        cell_size = input("Cell Size of code area polygon(10 m)-> ") or "10"
#        grid_size = input("Grid Size [m] (x,y dimension of the code area polygon rounded to be divisible by the cell size, e.g. 770,150)-> ") or "770,150"
#        z_pts = input("Zpts(10000 m) (any elevation notably higher than project max z) -> ") or "10000"

        z_pts = "10000"


        text = myfile.read().replace("NAME", NAME)
        text = text.replace("Cell Size == 10", "Cell Size == " + cell_size)
        text = text.replace("Grid Size (X,Y) == ",
                            "Grid Size (X,Y) == " + grid_size)                    
        text = text.replace("Set Zpts == 10000", "Set Zpts == " + z_pts)

        myfile.seek(0)
        myfile.write(text)
        myfile.truncate()
