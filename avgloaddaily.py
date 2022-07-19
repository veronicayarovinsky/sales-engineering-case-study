# avgloaddaily.py

import os
import pandas as pd
import datetime

print('-'*50)

MAIN_PATH = os.getcwd()
PROJECTDATA_PATH = MAIN_PATH + '/ProjectData'

def load_avg_daily():
    os.chdir(PROJECTDATA_PATH)
    inputfile = 'load.csv'
    df = pd.read_csv(inputfile, parse_dates = ['Timestamp'])
    df['day'] = df['Timestamp'].dt.day

    daily_df = pd.DataFrame(columns = ['Timestamp', 'Load kW', 'Load kVA'])

    prev_hr = df.loc[0, 'day']
    kW_sum = 0
    kVA_sum = 0
    num = 0

    for idx in range(len(df)):
        hr = df.loc[idx, 'day']
        if hr == prev_hr:
            kW_sum = kW_sum + float(df.loc[idx, 'Load kW'])
            kVA_sum = kW_sum + float(df.loc[idx, 'Load kVA'])
            num = num + 1
        else:
            kW_avg = kW_sum/num
            kVA_avg = kVA_sum/num
            timestamp = df.loc[idx-1, 'Timestamp']
            timestamp = timestamp.strftime('%m/%d/%Y')
            avg = pd.DataFrame({'Timestamp': [timestamp], 'Load kW': [format(kW_avg, '.2f')], 'Load kVA': [format(kVA_avg, '.2f')]})
            daily_df = pd.concat([daily_df, avg])

            prev_hr = df.loc[idx, 'day']

            kW_sum = float(df.loc[idx, 'Load kW'])
            kVA_sum = float(df.loc[idx, 'Load kVA'])
            num = 1

    kW_avg = kW_sum/num
    kVA_avg = kVA_sum/num
    timestamp = df.loc[idx-1, 'Timestamp']
    timestamp = timestamp.strftime('%m/%d/%Y')
    avg = pd.DataFrame({'Timestamp': [timestamp], 'Load kW': [format(kW_avg,'.2f')], 'Load kVA': [format(kVA_avg,'.2f')]})
    daily_df = pd.concat([daily_df, avg])

    outputfile = 'load_dailyavg.csv'
    daily_df.to_csv(outputfile, index=False)


load_avg_daily()