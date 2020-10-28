import os, sys
import pandas as pd
import csv
import subprocess

def run_tuflow(NAME, run_number):
    runs_folder = os.path.abspath("output_folder/" + NAME + "_tuflow/runs")
    model_folder = os.path.abspath("output_folder/" + NAME + "_tuflow/model")
    bc_dbase_path=os.path.abspath("output_folder/" + NAME + "_tuflow/bc_dbase")
    material_file=os.path.join(model_folder,"materials.csv")
    tgc_file=os.path.join(model_folder, NAME + ".tgc")

    for i in range(int(run_number)):
        current_run = "{0:0=3d}".format(i+1)
        with open(os.path.join(runs_folder + "/" + current_run, NAME + ".tcf"), 'r+') as myfile:
            text = myfile.read().replace("Write Empty GIS Files ", "! Write Empty GIS Files ")
            myfile.seek(0)
            myfile.write(text)
            myfile.truncate()

        with open(os.path.join(bc_dbase_path + "/" + current_run, "2d_bc_" + NAME + ".csv" ), 'r+') as myfile:
            text = myfile.read().replace("NAME_bc_data", NAME+"_bc_data")
            myfile.seek(0)
            myfile.write(text)
            myfile.truncate()
        
        with open(os.path.join(runs_folder + "/" + current_run, NAME + "_TUFLOW.bat" ), 'r+') as myfile:
            text = myfile.read().replace("NAME", current_run + "\\" + NAME)
            myfile.seek(0)
            myfile.write(text)
            myfile.truncate()

    
#    print("")
#    print("Material manning's n options")
#    print("")
#    print("1. gravel channel > 0.04")
#    print("2. cobble boulder channel > 0.06 ")
#    print("3. shrub > 0.01")
#    print("4. dense vegetation > 0.3")
#    print("5. enter your own manning's n")
#    material_ID= input("What is the Manning's n material ID? -> ")
    material_ID= '5'
    if material_ID=="5":
        fsd = pd.read_excel(os.path.abspath('output_folder/' + NAME + '_tuflow/flow_stage_depth.xlsx'))
        mannings_n= fsd['Man n'][0] # take the first one since they are all the same

        with open(material_file, 'r+') as myfile:
            text = myfile.read().replace("5,,,,!other", "5,{},,,!other".format(mannings_n))
            myfile.seek(0)
            myfile.write(text)
            myfile.truncate()
            myfile.close()
    with open(tgc_file, 'r+') as myfile:
        text = myfile.read().replace("Set Mat == 1", "Set Mat == {}".format(material_ID))
        myfile.seek(0)
        myfile.write(text)
        myfile.truncate()
        myfile.close()
    print("Running TUFLOW...")

    bc_data(NAME, run_number) 
    #create the input file (.csv) of inflow (RPin) and outflow elevation (RPout)

    # run tuflow sub process
    for i in range(int(run_number)):
        current_run = "{0:0=3d}".format(i+1)
        bat_file = os.path.join(runs_folder + "/" + current_run +'/' + NAME + "_TUFLOW.bat")
        p = subprocess.Popen(bat_file, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        p.communicate()
        print(current_run + " complete")


def bc_data(NAME, run_number):
    
    bc_dbase_path=os.path.abspath("output_folder/" + NAME + "_tuflow/bc_dbase")
    filename = NAME + '_bc_data.csv'
    with open(os.path.join("input_folder" + "/" + filename), 'r') as myfile:
    #with open( filename, 'r') as myfile:
        text = myfile.readlines()

    for i in range(int(run_number)):
        current_run = "{0:0=3d}".format(i+1)
# Create the input files (.csv) for each run
        data_path = os.path.join(bc_dbase_path + "/" + current_run)  # path in each run
        data_file = data_path +'/' + filename
        with open(data_file, 'w') as csvfile:
            csvfile.write(text[0]) # wrtire the colume names
            csvfile.write(text[(i +1)]) # wrtire the colume names
            csvfile.close()            
    

    
    
    
    
    