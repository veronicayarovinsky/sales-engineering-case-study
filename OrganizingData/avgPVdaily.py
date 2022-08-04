# avgPVdaily.py

import os
import pandas as pd
import datetime

print('-'*50)

MAIN_PATH = os.getcwd()
PROJECTDATA_PATH = MAIN_PATH + '/ProjectData'

def PV_data_hourly():
    os.chdir(PROJECTDATA_PATH)
    PV_data_file = 'PV_data.csv'
    parser = lambda date: datetime.datetime.strptime(date, '%d/%m/%Y %H:%M')
    df = pd.read_csv(PV_data_file, parse_dates = ['Hour'], date_parser = parser)
    df['day'] = df['Hour'].dt.day

    df_daily = pd.DataFrame(columns = ['Timestamp', 'Production (kW)'])

    prev_day = df.loc[0, 'day']
    kW_sum = 0
    num = 0
    for idx in range(len(df)):
        day = df.loc[idx, 'day']
        if day == prev_day:
            kW_sum = kW_sum + float(df.loc[idx, 'Production (kW)'])
            num = num + 1
        else:
            kW_avg = kW_sum/num
            timestamp = df.loc[idx-1, 'Hour']
            timestamp = timestamp.strftime('%m/%d/%Y')
            avg = pd.DataFrame({'Timestamp': [timestamp], 'Production (kW)': [format(kW_avg, '.2f')]})
            df_daily = pd.concat([df_daily, avg])

            prev_day = df.loc[idx, 'day']

            kW_sum = float(df.loc[idx, 'Production (kW)'])
            num = 1

    kW_avg = kW_sum/num
    timestamp = df.loc[idx-1, 'Hour']

    timestamp = timestamp.strftime('%m/%d/%Y')
    avg = pd.DataFrame({'Timestamp': [timestamp], 'Production (kW)': [format(kW_avg,'.2f')]})
    df_daily = pd.concat([df_daily, avg])

    outputfile = 'PV_dailyavg.csv'
    df_daily.to_csv(outputfile, index=False)


PV_data_hourly()