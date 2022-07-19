from json import load
import os
import math
import matplotlib
import numpy as np
import pandas as pd
import csv
import datetime

print('-'*50)

MAIN_PATH = os.getcwd()
PROJECTDATA_PATH = MAIN_PATH + '/ProjectData'

# parameters
DIESEL_PPL = 1              # diesel price per liter = $1
GENSET_COST_PER_KW = 400    # new genset cost = $0.4/W = $400/kW
NEW_GENSET_YRFREQ = 5       # need to purchase new gensets every 5 years
STANDBY_KW = 150
PRIME_KW = 135
CURR_NUM_GENSETS = 3

PV_LCOE = 0.05              # PV LCOE is $0.05/kWh
PV_SYSTEM_KW = 100          # size of PV system that data is provided for

KWH_2HR_BAT_COST = 500      # installed battery costs for 2hr system = $500/kWh
BAT_ADDHR_COST = 25         # every additional hour of storage = $25/kWh
BAT_EFFICIENCY = 0.88       # battery efficiency round trip

POWERFACTOR = 0.931         # from genset data: kW/kVA
STANDBY_KVA = 188
PRIME_KVA = 169

LIFETIME = 20


os.chdir(MAIN_PATH)
 

def main():

    os.chdir(PROJECTDATA_PATH)
    inputfile = 'load_dailyavg.csv'
    df = pd.read_csv(inputfile, parse_dates = ['Timestamp'])
    total_load = 0
    for idx in range(len(df)):
        load_kW = df.loc[idx, 'Load kW']
        total_load = total_load + load_kW

    dailyavg = total_load/len(df)

    daily_kWh = dailyavg * 24
    print('daily_kWh = ' + str(daily_kWh))


    # LOAD DATA FROM CSV INTO DATAFRAME
    os.chdir(PROJECTDATA_PATH)
    inputfile = 'hourlydata.csv'
    parser = lambda date: datetime.datetime.strptime(date, '%m/%d %H')
    df = pd.read_csv(inputfile, parse_dates = ['Timestamp'], date_parser = parser)

    PV_system_max = daily_kWh
    track_max_savings = 0
    results = []
    stepsize1 = 200
    PV_system_kW = 1

    with open('results_step1.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)

        PV_system_kW = 1
        while PV_system_kW < PV_system_max:
            bat_system_max = PV_system_kW
            PV_scaling_factor = PV_system_kW/PV_SYSTEM_KW
            bat_system_kWh = 1
            data = []
            while bat_system_kWh < bat_system_max:
                #print(PV_system_kW)
                #print(bat_system_kWh)
                total_net_savings = calc_netsavings(df, PV_scaling_factor, bat_system_kWh, LIFETIME)
                data.append(total_net_savings)

                if total_net_savings > track_max_savings:
                    results = [total_net_savings, PV_system_kW, bat_system_kWh]
                    track_max_savings = total_net_savings
                
                bat_system_kWh = bat_system_kWh + stepsize1

            csvwriter.writerow(data)
            PV_system_kW = PV_system_kW + stepsize1

    print(results)

    PV_system_kW_min = results[1] - stepsize1
    PV_system_kW_max = results[1] + stepsize1

    bat_system_kWh_min = results[2] - stepsize1
    bat_system_kWh_max = results[2] + stepsize1

    if bat_system_kWh_min < 0: bat_system_kWh_min = 1
    if bat_system_kWh_max < 0: bat_system_kWh_max = PV_system_kW_max

    print(PV_system_kW_min)
    print(PV_system_kW_max)
    print(bat_system_kWh_min)
    print(bat_system_kWh_max)

    stepsize2 = 20

    PV_system_kW = PV_system_kW_min

    with open('results_step2.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)

        while PV_system_kW < PV_system_kW_max:
            bat_system_max = PV_system_kW
            PV_scaling_factor = PV_system_kW/PV_SYSTEM_KW
            bat_system_kWh = bat_system_kWh_min

            data = []
            while bat_system_kWh < bat_system_kWh_max:
                #print(PV_system_kW)
                #print(bat_system_kWh)
                total_net_savings = calc_netsavings(df, PV_scaling_factor, bat_system_kWh, LIFETIME)
                data.append(total_net_savings)

                if total_net_savings > track_max_savings:
                    results = [total_net_savings, PV_system_kW, bat_system_kWh]
                    track_max_savings = total_net_savings
                
                bat_system_kWh = bat_system_kWh + stepsize2

            csvwriter.writerow(data)
            PV_system_kW = PV_system_kW + stepsize2

    print(results)


    PV_system_kW_min = results[1] - stepsize2
    PV_system_kW_max = results[1] + stepsize2

    bat_system_kWh_min = results[2] - stepsize2
    bat_system_kWh_max = results[2] + stepsize2

    if bat_system_kWh_min < 0: bat_system_kWh_min = 1
    if bat_system_kWh_max < 0: bat_system_kWh_max = PV_system_kW_max


    print(PV_system_kW_min)
    print(PV_system_kW_max)
    print(bat_system_kWh_min)
    print(bat_system_kWh_max)

    stepsize3 = 1

    PV_system_kW = PV_system_kW_min

    with open('results_step3.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        while PV_system_kW < PV_system_kW_max:
            bat_system_max = PV_system_kW
            PV_scaling_factor = PV_system_kW/PV_SYSTEM_KW
            bat_system_kWh = bat_system_kWh_min

            data = []
            while bat_system_kWh < bat_system_kWh_max:
                #print(PV_system_kW)
                #print(bat_system_kWh)
                total_net_savings = calc_netsavings(df, PV_scaling_factor, bat_system_kWh, LIFETIME)
                data.append(total_net_savings)

                if total_net_savings > track_max_savings:
                    results = [total_net_savings, PV_system_kW, bat_system_kWh]
                    track_max_savings = total_net_savings
                
                bat_system_kWh = bat_system_kWh + stepsize3

            csvwriter.writerow(data)
            PV_system_kW = PV_system_kW + stepsize3

    print(results)


    # RUNNING THE MODEL WITH THE OPTIMAL RESULTS HARDCODED
    # PV_system_kW = 1000
    # bat_system_kWh = 350
    # PV_scaling_factor = PV_system_kW/PV_SYSTEM_KW
    # total_net_savings = calc_netsavings(df, PV_scaling_factor, bat_system_kWh, LIFETIME)



def calc_netsavings(df, PV_scaling_factor, bat_system_kWh, totalyrs):
    #print('_'*40)
    
    # INITIALIZE TRACKERS
    PV_kWh = 0                  # keeps track of total kWh supplied by PV over time period in csv, used for calculating PV cost
    
    total_addhrs_batstorage = 0 # keeps track of the additional hrs of battery (above baseline 2hrs), used for calculating battery cost
    bat_stored_kWh = 0          # tracks kWh of charge remaining on battery
    numhrs_bat_stored = 0       # number of hours that battery stores energy for (resets when battery is drained)
    max_numhrs_bat = 0          # tracks max number of hours that battery stores energy for
    bat_size_exceeded_ctr = 0   # counts number of times that PV supplies excess power that cannot be stored in battery due to battery size limitation
    
    num_gensets_used = 0        # keeps track of number of gensets needed at most
    curr_annualcost = 0         # used for calculating total diesel cost of current system (no PV)
    genset_annualcost = 0       # used for calculating total diesel cost with implemented system

    num_hrs = 1                 # for converting from kW to kWh (little significance since looking at hourly data)
    

    # ITERATE THROUGH ROWS IN DF (EACH HOUR OF DATA)
    for idx in range(len(df)):

        # extract PV and load data from df
        PV_production_kWh = df.loc[idx, 'Production (kW)'] * PV_scaling_factor * num_hrs
        load_kWh = df.loc[idx, 'Load kW'] * num_hrs

        # calculate current annual cost (diesel only)
        curr_d_cost = get_d_cost('prime', load_kWh, num_hrs)[0]                 # current system fulfills entire load with only diesel, with generators in prime fuel consump bc gensets = only source of power
        curr_annualcost = curr_annualcost + curr_d_cost

        # sums total energy produced from PV
        if PV_production_kWh > 0:
            PV_kWh = PV_kWh + PV_production_kWh

        # excess energy produced by PV
        if PV_production_kWh >= load_kWh:                                       
            excessload_kWh = PV_production_kWh - load_kWh
            if bat_stored_kWh < bat_system_kWh:                                 # PV production + battery storage can't be greater than battery bank size -- note when this happens!!
                bat_storage_remaining = bat_system_kWh
                if bat_storage_remaining < excessload_kWh:
                    bat_stored_kWh = bat_system_kWh
                else:
                    bat_stored_kWh = bat_stored_kWh + excessload_kWh
            else:
                bat_size_exceeded_ctr = bat_size_exceeded_ctr + 1
                #print('exceeded battery bank size') 
            numhrs_bat_stored = numhrs_bat_stored + 1                           # counts current hour as an hour that needs to be stored


        # energy produced by PV does not meet energy need --> batteries or gensets must be used
        if PV_production_kWh < load_kWh:                                        
            remainingload_kWh = load_kWh - PV_production_kWh                    # deplete battery charge entirely, then use gensets --> minimizes cost of additional hrs of battery storage

            if remainingload_kWh <= (BAT_EFFICIENCY * bat_stored_kWh):          # all remaining load can be supplied with battery
                bat_stored_kWh = (BAT_EFFICIENCY * bat_stored_kWh) - remainingload_kWh
                if bat_stored_kWh > 0:                                          # if remaining load is exactly the same as energy battery contains, battery is depleted
                    numhrs_bat_stored = numhrs_bat_stored + 1

            if remainingload_kWh > (bat_stored_kWh * BAT_EFFICIENCY):           # battery insufficient, gensets needed

                # part of the load is supplied by the battery (until the battery is drained)
                remainingload_kWh = remainingload_kWh - (BAT_EFFICIENCY * bat_stored_kWh)
                numhrs_bat_stored = 0                       # battery drained

                # the rest of the load is supplied by gensets
                d_kWh_need = remainingload_kWh                                  # energy (kWh) that diesel must supply

                array = get_d_cost('standby', d_kWh_need, num_hrs)              # diesel cost for this timeframe
                d_cost = array[0]
                genset_annualcost = genset_annualcost + d_cost                  # add to total diesel cost

                num_gensets = array[1]
                if num_gensets_used < num_gensets:
                    num_gensets_used = num_gensets

        # calculate hours of battery storage (above the 2 hrs provided by baseline battery system)
        if numhrs_bat_stored > 2:
            total_addhrs_batstorage = total_addhrs_batstorage + (numhrs_bat_stored - 2)
            if numhrs_bat_stored > max_numhrs_bat:
                max_numhrs_bat = numhrs_bat_stored

    # print('max_numhrs_bat: ' + str(max_numhrs_bat))
    # print('bat_size_exceeded_ctr: ' + str(bat_size_exceeded_ctr))


    # CALCULATE COSTS
    # annual costs
    # print('current annual diesel cost is ' + str(curr_annualcost))

    PV_annualcost = PV_kWh * PV_LCOE
    # print('annual PV cost is ' + str(PV_annualcost))

    # print('new annual diesel cost is ' + str(genset_annualcost))

    # fixed costs
    bat_fixedcost = (KWH_2HR_BAT_COST * bat_system_kWh) + (BAT_ADDHR_COST * max_numhrs_bat * bat_system_kWh)    # once in lifetime
    # print('fixed battery cost is ' + str(bat_fixedcost))

    genset_fixedcost = STANDBY_KW * GENSET_COST_PER_KW                                                  # every 5 years
    # print('genset standby genset fixed cost = ' + str(genset_fixedcost))

    curr_genset_fixedcost = PRIME_KW * GENSET_COST_PER_KW
    # print('current prime genset fixed cost = ' + str(curr_genset_fixedcost))                            # every 5 years

    # CALCULATE TOTAL NET SAVINGS FOR GIVEN NUMBER OF YEARS
    year = 0
    total_net_savings = 0
    while year < totalyrs:
        if year == 0:
            fixed_cost_new = bat_fixedcost + genset_fixedcost
            fixed_cost_old = curr_genset_fixedcost
        elif year % 5 == 0:
            fixed_cost_new = genset_fixedcost
            fixed_cost_old = curr_genset_fixedcost
        else:
            fixed_cost_new = 0
            fixed_cost_old = 0
        
        annual_cost_new = PV_annualcost + genset_annualcost
        net_savings = (fixed_cost_old + curr_annualcost) - (fixed_cost_new + annual_cost_new)
        # print('year ' + str(year) + ': net savings = ' + str(net_savings))

        total_net_savings = total_net_savings + net_savings
        # print(total_net_savings)
        year = year + 1


    return total_net_savings
        


# DIESEL
def get_d_cost(fuel_consump, d_load_kW, num_hrs):

    new_d_load_kW = d_load_kW
    new_d_load_kVA = new_d_load_kW / POWERFACTOR
    num_gensets = 1

    if fuel_consump == 'standby':

        # calculate number of generators needed for load, since load cannot exceed generator ratings
        while (new_d_load_kW - STANDBY_KW) > 0 or (new_d_load_kVA - STANDBY_KW) > 0:
            num_gensets = num_gensets + 1
            new_d_load_kW = new_d_load_kW - STANDBY_KW
            new_d_load_kVA = new_d_load_kVA - STANDBY_KVA

        # diesel cost calculated from kVA bc that is power input (fuel needs)
        if num_gensets == 1:
            d_L_per_hr = (-9.6 * (new_d_load_kVA/STANDBY_KVA)**2) + (50.6 * (new_d_load_kVA/STANDBY_KVA)) + 3.35
            d_L = d_L_per_hr * num_hrs
            d_cost = d_L * DIESEL_PPL
        
        if num_gensets == 2:
            d_L_per_hr = (-9.6 * (1)**2) + (50.6 * (1)) + 3.35
            d_L = d_L_per_hr * num_hrs
            d_cost = d_L * DIESEL_PPL * (num_gensets - 1)
            d_L_per_hr = (-9.6 * (new_d_load_kVA/STANDBY_KVA)**2) + (50.6 * (new_d_load_kVA/STANDBY_KVA)) + 3.35
            d_L = d_L_per_hr * num_hrs
            d_cost = d_cost + (d_L * DIESEL_PPL)

        if num_gensets == 3:
            d_L_per_hr = (-9.6 * (2)**2) + (50.6 * (2)) + 3.35
            d_L = d_L_per_hr * num_hrs
            d_cost = d_L * DIESEL_PPL * (num_gensets - 1)
            d_L_per_hr = (-9.6 * (new_d_load_kVA/STANDBY_KVA)**2) + (50.6 * (new_d_load_kVA/STANDBY_KVA)) + 3.35
            d_L = d_L_per_hr * num_hrs
            d_cost = d_cost + (d_L * DIESEL_PPL)


    elif fuel_consump == 'prime':

        # calculate number of generators needed for load, since load cannot exceed generator ratings
        while (new_d_load_kW - PRIME_KW) > 0 or (new_d_load_kVA - PRIME_KW) > 0:
            num_gensets = num_gensets + 1
            new_d_load_kW = new_d_load_kW - PRIME_KW
            new_d_load_kVA = new_d_load_kVA - PRIME_KVA

        # diesel cost calculated from kVA bc that is power input (fuel needs)
        if num_gensets == 1:
            d_L_per_hr = (-6 * (new_d_load_kVA/PRIME_KVA)**2) + (42.7 * (new_d_load_kVA/PRIME_KVA)) + 4.33
            d_L = d_L_per_hr * num_hrs
            d_cost = d_L * DIESEL_PPL
        
        if num_gensets == 2:
            d_L_per_hr = (-6 * (1)**2) + (42.7 * (1)) + 4.33
            d_L = d_L_per_hr * num_hrs
            d_cost = d_L * DIESEL_PPL * (num_gensets - 1)
            d_L_per_hr = (-6 * (new_d_load_kVA/PRIME_KVA)**2) + (42.7 * (new_d_load_kVA/PRIME_KVA)) + 4.33
            d_L = d_L_per_hr * num_hrs
            d_cost = d_cost + (d_L * DIESEL_PPL)

        if num_gensets == 3:
            d_L_per_hr = (-6 * (1)**2) + (42.7 * (1)) + 4.33
            d_L = d_L_per_hr * num_hrs
            d_cost = d_L * DIESEL_PPL * (num_gensets - 1)
            d_L_per_hr = (-6 * (new_d_load_kVA/PRIME_KVA)**2) + (42.7 * (new_d_load_kVA/PRIME_KVA)) + 4.33
            d_L = d_L_per_hr * num_hrs
            d_cost = d_cost + (d_L * DIESEL_PPL)

    array = [d_cost, num_gensets]
    return array




main()