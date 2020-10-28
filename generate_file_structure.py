import os
import errno
import subprocess
from shutil import rmtree, copyfile, copy2, copytree, copy


def generate_file_structure(NAME, run_number):

    output_folder = os.path.abspath("output_folder/" + NAME + "_tuflow/")
    bc_dbase_folder_init = os.path.abspath(
        "output_folder/" + NAME + "_tuflow/bc_dbase/init")
    bc_dbase_folder = os.path.abspath(
        "output_folder/" + NAME + "_tuflow/bc_dbase/")
    model_folder = os.path.abspath("output_folder/" + NAME + "_tuflow/model/")
    runs_folder_init = os.path.abspath("output_folder/" + NAME + "_tuflow/runs/init/")
    runs_folder = os.path.abspath("output_folder/" + NAME + "_tuflow/runs/")
    check_folder_init = os.path.abspath("output_folder/" + NAME + "_tuflow/check/init/")
    results_folder_init = os.path.abspath("output_folder/" + NAME + "_tuflow/results/init/")
    check_folder = os.path.abspath("output_folder/" + NAME + "_tuflow/check/")
    results_folder = os.path.abspath("output_folder/" + NAME + "_tuflow/results/")
    grid_folder = os.path.abspath("output_folder/" + NAME + "_tuflow/model/grid/")
    gis_folder = os.path.abspath("output_folder/" +  NAME + "_tuflow/model/gis/")
    sfcomponents = ['CPG', 'dbf', 'prj', 'sbn', 'sbx', 'shp', 'shp.xml', 'shx',]

    # edit NAME to actual name in tuflow.bat
    bat_file_path = os.path.join(
        runs_folder_init, NAME + "_TUFLOW.bat")

    if os.path.isdir("output_folder/" + NAME + "_tuflow"):
        rmtree("output_folder/" + NAME + "_tuflow")
    

    # copy everything from template folder to output folder
    #copytree("C:/Git_hub/tuflow-wf_python3/template", output_folder) updated 9/4/20
    copytree("F:/tuflow-wf_python3/template", output_folder)
    copyfile("input_folder/" + NAME + ".asc", os.path.join(grid_folder, NAME + ".asc"))
    copyfile("input_folder/" + NAME + ".prj", os.path.join(grid_folder, NAME + ".prj"))
    # copyfile("flow_stage_depth.xlsx",os.path.join(output_folder,"flow_stage_depth.xlsx"))
    os.rename(os.path.join(bc_dbase_folder_init, "2d_bc_NAME.csv"),
              os.path.join(bc_dbase_folder_init, "2d_bc_"+NAME+".csv"))
    os.rename(os.path.join(bc_dbase_folder_init, "NAME_bc_data.csv"),
              os.path.join(bc_dbase_folder_init, NAME+"_bc_data.csv"))
    os.rename(os.path.join(model_folder, "NAME.tbc"),
              os.path.join(model_folder, NAME + ".tbc"))
    os.rename(os.path.join(model_folder, "NAME.tgc"),
              os.path.join(model_folder, NAME + ".tgc"))
    os.rename(os.path.join(runs_folder_init, "NAME_TUFLOW.bat"),
              os.path.join(runs_folder_init, NAME + "_TUFLOW.bat"))
    os.rename(runs_folder_init + "/NAME.tcf",
              runs_folder_init + "/" + NAME + ".tcf")

####Daniel's insertion of code begins -------------------------
    for i in sfcomponents:
        os.rename(os.path.join(gis_folder, "2d_xsect_name_L." + i),
                  os.path.join(gis_folder, "2d_xsect_" + NAME + "_L." + i))
        os.rename(os.path.join(gis_folder, "2d_trim_name_R." + i),
                  os.path.join(gis_folder, "2d_trim_" + NAME + "_R." + i))
######  Daniel's insertion of code ends--------------------------------------

   # Open .bat file and rewrite the name of the .tcf file in run/init    
    with open(os.path.join(bat_file_path), 'r+') as myfile:
        text = myfile.read().replace("TUFLOW_OUTPUT_FOLDER", output_folder)
        text = text.replace("runs\\NAME", "runs\\init\\" + NAME)
        myfile.seek(0)
        myfile.write(text)
        myfile.truncate()

    
    for num in range(int(run_number)):
        copytree(bc_dbase_folder_init, bc_dbase_folder +  '\\' + "{0:0=3d}".format(num+1) )
        copytree(runs_folder_init, runs_folder +  '\\' + "{0:0=3d}".format(num+1))
        copytree(check_folder_init, check_folder +  '\\' + "{0:0=3d}".format(num+1))
        copytree(results_folder_init, results_folder + '\\' + "{0:0=3d}".format(num+1))
        # Open .bat file in run# folder and rewrite it    
        run_bat_file_path = bat_file_path.replace('init', "{0:0=3d}".format(num+1)) 
        with open(os.path.join( run_bat_file_path), 'r+') as myfile:
            text = myfile.read().replace("init","\\" + "{0:0=3d}".format(num+1))
            myfile.seek(0)
            myfile.write(text)
            myfile.truncate()

    # step 2.5
    copyfile("output_folder/shp_files/" + NAME + "_bound_rec.prj",
             model_folder + "/gis/Projection.prj")



    # run tuflow sub process
    p = subprocess.Popen(bat_file_path, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    p.communicate()

#    empty_files = os.listdir(model_folder)
#    print(empty_files)

