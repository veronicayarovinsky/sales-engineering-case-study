# avgbyhour.py - create daily profile for PV and load

import os
import pandas as pd
import csv

print('-'*50)

MAIN_PATH = os.getcwd()
PROJECTDATA_PATH = MAIN_PATH + '/ProjectData'


def main():
    os.chdir(PROJECTDATA_PATH)
    dailyprofile('PV_data_hourly.csv', 'PV_dailyprofile.csv', 'Timestamp', 'Production (kW)')
    dailyprofile('load.csv', 'load_dailyprofile.csv', 'Timestamp', 'Load kW')


def dailyprofile(inputfile, outputfile, time_col, kW_col):
    df = pd.read_csv(inputfile, parse_dates = [time_col])
    df['hour'] = df[time_col].dt.hour

    dict = {}

    for idx in range(len(df)):
        hr = df.loc[idx, 'hour']
        kW = df.loc[idx, kW_col]
        if kW == '#DIV/0!':
            print(idx)
        if hr not in dict:
            dict[hr] = [kW]
        else:
            array = dict[hr]
            array.append(kW)

    new_dict = {}
    
    for key in dict:
        sum = 0
        array = dict[key]
        for item in array:
            sum = sum + float(item)
        avg = sum/len(array)
        new_dict[key] = [format(avg, '0.4f')]

    new_df = pd.DataFrame.from_dict(new_dict, orient='index')
    new_df.to_csv(outputfile, index=False, header=False)


main()