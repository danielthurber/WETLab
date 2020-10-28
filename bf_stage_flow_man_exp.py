import os
import sys
import simpledbf
import arcpy
import pandas as pd
import numpy as np
import _thread
import matplotlib.pyplot as plt
from scipy import interpolate as int
#for console runs:   args = [NAME, stages, S, n, Elevation, bf_wse]



def stage_flow_inputs_mannings_exp(*args):
    # This function calculates stage and discharge for proportions of bankfull depth.
    # It can be called in 3 different ways:
    #       stage_flow_inputs_mannings(NAME, props_bf, slope, n, dnstream_bed_el)
    #           Since this method does not have a specified bankfull depth or water surface elevation,
    #           one must be specified. A plot of the transect specified will appear, and the user
    #           must enter the water surface elevation at bankfull and the average bed elevation at
    #           the transect so that it can be determined.
    #       stage_flow_inputs_mannings(NAME, props_bf, slope, n, dnstream_bed_el, bf_stage, tsect_bed_el)
    #           This is added so that the user doesn't have to input bankfull water surface and average
    #           transect bed elevation in the command line every time. If these two are read in, the
    #           function performs the calculations automatically.
    #
    # The required inputs are:
    #   NAME            - the string that corresponds with the TUFLOW run name from main script
    #   props_bf        - a numpy array containing the set of proportions of bankfull to be run
    #   slope           - the average slope of the bed in the reach
    #   n               - Manning's roughness n
    #   dnstream_bed_el - The bed elevation in meters at the downstream-most transect of the reach. This is
    #                       needed to calculate depth at the downstream-most transect so the model can
    #                       be confined.
    # The optional inputs are:
    #   bf_stage        - the water surface elevation of bankfull depth
    #   tsect_bed_el    - the average bed elevation at the transect of interest


    NAME = args[0] #The text that names the TUFLOW run
    props_bf = args[1] #the list of proportions of bankfull as a numpy array
    slope = args[2] #average slope for manning's equation
    n = args[3] # manning's n
    dnstream_bed_el = args[4]

    xsectshp = './output_folder/' + NAME + '_tuflow/model/gis/2d_xsect_' + NAME + '_L.shp'
    terrain = './input_folder/' + NAME + '.asc'
    xsecttab = './output_folder/' + NAME + '_tuflow/model/gis/2d_xsect_' + NAME + '_table.dbf'
    if not(os.path.isfile(xsectshp)):
        print(xsectshp + ' is not found. Please create a polyline in arcGIS and save it in this location.')
        _thread.interrupt_main()

    if os.path.isfile(xsecttab):
        os.remove(xsecttab)     #delete xsect table
    arcpy.CheckOutExtension('3D')
    arcpy.StackProfile_3d(xsectshp, profile_targets=[terrain], out_table=xsecttab) #create new xsect table
    xsectdbf = simpledbf.Dbf5(xsecttab)
    xsectdfst = xsectdbf.to_dataframe()
    #add radius column to xsect table and identify minimum elev
    xsectdfst['radius'] = np.sqrt(xsectdfst['FIRST_DIST'].diff(periods=-1)**2 + xsectdfst['FIRST_Z'].diff(periods=-1)**2)
    tsect_bed_el = min(xsectdfst['FIRST_Z'])

    #copied from method == 2
    f = int.interp1d(xsectdfst['FIRST_DIST'], xsectdfst['FIRST_Z'], kind='linear')
    intdts = np.arange(xsectdfst['FIRST_DIST'].min(), xsectdfst['FIRST_DIST'].max(), 0.01)
    intels = f(intdts)

    xsectdf = pd.DataFrame({"FIRST_DIST": intdts, "FIRST_Z": intels})
    xsectdf['radius'] =  np.sqrt(xsectdf['FIRST_DIST'].diff(periods=-1)**2 + xsectdf['FIRST_Z'].diff(periods=-1)**2)

    # xsectdf contains all interpolated points

    #create, display, and save plot of xsect bed elevation profile
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)
    ax1.set_title('Cross Section from Shapefile\n' +
                  'Get elevation of bankfull and average bed elevation to enter into command prompt\n' +
                  'After closing plot window')
    linec = ax1.plot(xsectdf['FIRST_DIST'], xsectdf['FIRST_Z'], 'k.-')
    ax1.set_xlabel('Lateral Distance (m)')
    ax1.set_ylabel('Elevation (m)')
    plt.savefig('./output_folder/' + NAME + '_tuflow/' + NAME + '_xsect_profile.png')
    plt.show()
    if len(args)==5:
        # require user to input either bankfull stage and confirm bf bed elevation
        bf_stage = float(input('Enter elevation of Bankfull Water Surface (Value from Y-Axis of Plot): '))
        input('Minimum bed elevation is ' + str(tsect_bed_el) + '.  Press ENTER to confirm')
        bf_depth = bf_stage - tsect_bed_el
    elif len(args)==6:
        bf_stage = args[5]
        bf_depth = bf_stage - tsect_bed_el
    else:
        sys.exit('Incorrect number of inputs to generate flow rating curve.')

    print('Bankfull depth = ' +str(bf_depth))
    # bf_stage = min_bed_el + bf_depth
    # bf_depth = bf_stage - min_bed_el
    output_data = pd.DataFrame(columns = ['Proportion BF','Depth (m)','Transect Stage','Downstream Stage',
                                          'Area','Perimeter','Hyd Radius','Man n','Q (cms)'],
                                index=range(len(props_bf)))
    for i in range(len(props_bf)):

        output_data['Proportion BF'][i] = props_bf[i]
        output_data['Depth (m)'][i] = bf_depth * props_bf[i]
        output_data['Transect Stage'][i] = tsect_bed_el + output_data['Depth (m)'][i] # The WSE at the transect
        output_data['Downstream Stage'][i] = dnstream_bed_el + output_data['Depth (m)'][i] # The WSE at the downstream-most transect
        xsectdf['area'] = abs(xsectdf['FIRST_DIST'].diff() * (output_data['Transect Stage'][i] - xsectdf['FIRST_Z']))
        output_data['Perimeter'][i] = sum(xsectdf['radius'][xsectdf['FIRST_Z'] < output_data['Transect Stage'][i]])
        print('Perimeter ' + str(i) + ' = ' + str(output_data['Perimeter'][i]))
        output_data['Area'][i] = sum(xsectdf['area'][xsectdf['FIRST_Z'] < output_data['Transect Stage'][i]])
        output_data['Hyd Radius'][i] = output_data['Area'][i]/output_data['Perimeter'][i]
        output_data['Man n'][i] = n
        output_data['Q (cms)'][i] = (1/n) * output_data['Area'][i] * slope**(1/2) * output_data['Hyd Radius'][i]**(2/3)

    output_data.to_excel("./output_folder/"+NAME+"_tuflow/flow_stage_depth.xlsx")
    bc_data = pd.DataFrame({'Time': np.zeros_like(props_bf), 'RPin': output_data['Q (cms)'], 'RPout': output_data['Downstream Stage']})
    bc_data = bc_data.set_index('Time')
    bc_data.to_csv('./input_folder/' + NAME + '_bc_data.csv')
