# avgPVhourly.PY - averages PV data hourly using the 5 minute data in order to match with the hourly load data
# input file: PV_data.csv
# output file: PV_data_hourly.csv

import os
import pandas as pd
import datetime

print('-'*50)

MAIN_PATH = os.getcwd()
PROJECTDATA_PATH = MAIN_PATH + '/ProjectData'

def PV_data_hourly():
    os.chdir(PROJECTDATA_PATH)
    PV_data_file = 'PV_data.csv'
    parser = lambda date: datetime.datetime.strptime(date, '%d/%m/%Y %H:%M')        # since timestamp format differs from norm
    df = pd.read_csv(PV_data_file, parse_dates = ['Hour'], date_parser = parser)    # load the data into a csv
    df['hour'] = df['Hour'].dt.hour                                                 # add separate column in df for hour of the timestamp

    hourly_df = pd.DataFrame(columns = ['Timestamp', 'Production (kW)'])            # create separate df for hourly averages

    prev_hr = df.loc[0, 'hour']
    kW_sum = 0
    num = 0

    for idx in range(len(df)):
        hr = df.loc[idx, 'hour']
        if hr == prev_hr:
            kW_sum = kW_sum + float(df.loc[idx, 'Production (kW)'])
            num = num + 1
        else:
            kW_avg = kW_sum/num
            timestamp = df.loc[idx-1, 'Hour']
            timestamp = timestamp.strftime('%m/%d %H')

            avg = pd.DataFrame({'Timestamp': [timestamp], 'Production (kW)': [format(kW_avg, '.2f')]})
            hourly_df = pd.concat([hourly_df, avg])

            prev_hr = df.loc[idx, 'hour']

            kW_sum = float(df.loc[idx, 'Production (kW)'])
            num = 1

    kW_avg = kW_sum/num
    timestamp = df.loc[idx-1, 'Hour']
    timestamp = timestamp.strftime('%m/%d %H')
    avg = pd.DataFrame({'Timestamp': [timestamp], 'Production (kW)': [format(kW_avg,'.2f')]})
    hourly_df = pd.concat([hourly_df, avg])

    outputfile = 'PV_data_hourly.csv'
    hourly_df.to_csv(outputfile, index=False)


PV_data_hourly()