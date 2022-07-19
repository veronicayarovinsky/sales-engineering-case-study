# COMBINEDATA.PY - combines the load data and the PV hourly data into a csv file to be used in the model
# input files: PV_data_hourly.csv and load.csv
# output file: hourlydata.csv

import os
import pandas as pd
import datetime

print('-'*50)

MAIN_PATH = os.getcwd()
PROJECTDATA_PATH = MAIN_PATH + '/ProjectData'

def combinedata():
    os.chdir(PROJECTDATA_PATH)
    PV_file = 'PV_data_hourly.csv'
    load_file = 'load.csv'

    df_PV = pd.read_csv(PV_file)
    df_load = pd.read_csv(load_file)

    df_PV['Load kW'] = df_load['Load kW']
    df_PV['Load kVA'] = df_load['Load kVA']

    outputfile = 'hourlydata.csv'
    df_PV.to_csv(outputfile, index=False)


combinedata()