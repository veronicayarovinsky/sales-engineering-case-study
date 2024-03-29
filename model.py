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
RESULTS_PATH = MAIN_PATH + '/Results'

# parameters
DIESEL_PPL = 1              # diesel price per liter = $1
GENSET_COST_PER_KW = 400    # new genset cost = $0.4/W = $400/kW
NEW_GENSET_YRFREQ = 5       # need to purchase new gensets every 5 years
STANDBY_KW = 150
PRIME_KW = 135
CURR_NUM_GENSETS = 3

PV_LCOE = 0.05              # PV LCOE is $0.05/kWh
PV_SYSTEM_KW = 100          # size of PV system that data is provided for
PV_PANEL_WATTAGE = 0.4      # each PV panel added to system has a wattage of 0.4 kW

KWH_2HR_BAT_COST = 500      # installed battery costs for 2hr system = $500/kWh
BAT_ADDHR_COST = 25         # every additional hour of storage = $25/kWh

POWERFACTOR = 0.931         # from genset data: kW/kVA
STANDBY_KVA = 188
PRIME_KVA = 169

LIFETIME = 20


os.chdir(MAIN_PATH)
 

def main():

    os.chdir(PROJECTDATA_PATH)

    ###########################################################

    # calculate average daily energy consumption (limits range of reasonable values for PV System)
    inputfile = 'load_dailyavg.csv'
    df = pd.read_csv(inputfile, parse_dates = ['Timestamp'])
    total_load = 0
    for idx in range(len(df)):
        load_kW = df.loc[idx, 'Load kW']
        total_load = total_load + load_kW

    dailyavg = total_load/len(df)

    daily_kWh = dailyavg * 24                                       
    # print('daily_kWh = ' + str(daily_kWh))

    ###########################################################

    # load hourly data for PV Production and Load from csv into Dataframe
    inputfile = 'hourlydata.csv'
    parser = lambda date: datetime.datetime.strptime(date, '%m/%d %H')
    df = pd.read_csv(inputfile, parse_dates = ['Timestamp'], date_parser = parser)

    ###########################################################

    # Optimization

    # variables:
        # PV system size
        # BESS duration
        # Number of Batteries

    os.chdir(RESULTS_PATH)

    bess_duration = 2       # hrs

    # optimize for both BESS & PV
    PV_system_max = daily_kWh
    track_max_savings = 0
    stepsize1 = 100
    PV_system_kW = PV_SYSTEM_KW
    num_bess = 1
    max_num_bess = 4

    outputfile1 = 'results1.csv'
    results = optimize_BESS_PV(outputfile1, df, bess_duration, num_bess, max_num_bess, PV_system_kW, PV_system_max, track_max_savings, stepsize1)
    print(results)

    track_max_savings = results[0]
    optimal_num_bess = results[2]             # conclude optimal BESS scaling factor


    # optimize for only PV but narrowed down and with step size = 10
    stepsize2 = 10
    PV_system_kW_min = results[1] - stepsize1
    PV_system_kW_max = results[1] + stepsize1

    outputfile2 = 'results2.csv'
    results = optimize_PV(outputfile2, df, bess_duration, optimal_num_bess, PV_system_kW_min, PV_system_kW_max, track_max_savings, stepsize2)
    print(results)
    

    # optimize for only PV but narrowed down again an with step size = PV Panel Wattage
    stepsize3 = PV_PANEL_WATTAGE
    PV_system_kW_min = results[1] - stepsize2
    PV_system_kW_max = results[1] + stepsize2

    outputfile3 = 'results3.csv'
    results = optimize_PV(outputfile3, df, bess_duration, optimal_num_bess, PV_system_kW_min, PV_system_kW_max, track_max_savings, stepsize3)
    print(results)


    ###########################################################

    # repeat with BESS duration = 4 hours
    bess_duration = 4       # hrs

    # optimize for both BESS & PV
    PV_system_max = daily_kWh
    track_max_savings = 0
    stepsize1 = 100
    PV_system_kW = PV_SYSTEM_KW
    num_bess = 1
    max_num_bess = 4

    outputfile4 = 'results4.csv'
    results = optimize_BESS_PV(outputfile4, df, bess_duration, num_bess, max_num_bess, PV_system_kW, PV_system_max, track_max_savings, stepsize1)
    print(results)

    track_max_savings = results[0]
    optimal_num_bess = results[2]             # conclude optimal BESS scaling factor

    
    # optimize for only PV but narrowed down and with step size = 10
    stepsize2 = 10
    PV_system_kW_min = results[1] - stepsize1
    PV_system_kW_max = results[1] + stepsize1

    outputfile5 = 'results5.csv'
    results = optimize_PV(outputfile5, df, bess_duration, optimal_num_bess, PV_system_kW_min, PV_system_kW_max, track_max_savings, stepsize2)
    print(results)


    # optimize for only PV but narrowed down again an with step size = PV Panel Wattage
    stepsize3 = PV_PANEL_WATTAGE
    PV_system_kW_min = results[1] - stepsize2
    PV_system_kW_max = results[1] + stepsize2

    outputfile6 = 'results6.csv'
    results = optimize_PV(outputfile6, df, bess_duration, optimal_num_bess, PV_system_kW_min, PV_system_kW_max, track_max_savings, stepsize3)
    print(results)

    
    ###########################################################

    # RUNNING THE MODEL WITH THE OPTIMAL RESULTS HARDCODED
    print('-'*50)
    PV_system_kW = 1420
    bess_duration = 2
    optimal_num_bess = 1
    PV_scaling_factor = PV_system_kW/PV_SYSTEM_KW
    total_net_savings = calc_netsavings(df, PV_scaling_factor, bess_duration, optimal_num_bess, LIFETIME)



###########################################################################################

def optimize_BESS_PV(outputfile, df, bess_duration, num_bess, max_num_bess, PV_system_kW, PV_system_max, track_max_savings, stepsize):

    with open(outputfile, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)

        while num_bess <= max_num_bess:
            data = []
            while PV_system_kW <= PV_system_max:
                PV_scaling_factor = PV_system_kW/PV_SYSTEM_KW
                total_net_savings = calc_netsavings(df, PV_scaling_factor, bess_duration, num_bess, LIFETIME)
                # print(total_net_savings)
                data.append(total_net_savings)

                if total_net_savings > track_max_savings:
                    results = [total_net_savings, PV_system_kW, num_bess]
                    track_max_savings = total_net_savings
                
                PV_system_kW = PV_system_kW + stepsize
            
            csvwriter.writerow(data)
            num_bess = num_bess + 1

    return results



###########################################################################################

def optimize_PV(outputfile, df, bess_duration, optimal_num_bess, PV_system_kW_min, PV_system_kW_max, track_max_savings, stepsize):
    PV_system_kW = PV_system_kW_min

    with open(outputfile, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        
        while PV_system_kW <= PV_system_kW_max:
                PV_scaling_factor = PV_system_kW/PV_SYSTEM_KW
                total_net_savings = calc_netsavings(df, PV_scaling_factor, bess_duration, optimal_num_bess, LIFETIME)

                data = [PV_system_kW, total_net_savings]
                csvwriter.writerow(data)

                if total_net_savings > track_max_savings:
                    results = [total_net_savings, PV_system_kW, optimal_num_bess]
                    track_max_savings = total_net_savings

                PV_system_kW = PV_system_kW + stepsize

    return results



###########################################################################################

def calc_netsavings(df, PV_scaling_factor, bess_duration, num_bess, totalyrs):
    
    # INITIALIZE TRACKERS
    PV_kWh = 0                  # keeps track of total kWh supplied by PV over time period in csv, used for calculating PV cost
    
    bess_kWh_stored = 0          # tracks kWh of charge remaining on battery
    
    num_gensets_used = 0        # keeps track of number of gensets needed at most
    curr_annualcost = 0         # used for calculating total diesel cost of current system (no PV)
    genset_annualcost = 0       # used for calculating total diesel cost with implemented system

    num_hrs = 1                 # for converting from kW to kWh (little significance since looking at hourly data)


    # based on Megapack specs
    if bess_duration == 2:
        bess_power = 1295 * num_bess         # kW
        bess_energy = 2570 * num_bess        # kWh
        bess_efficiency = 0.92
    if bess_duration == 4:
        bess_power = 775 * num_bess          # kW
        bess_energy = 3101 * num_bess        # kWh
        bess_efficiency = 0.935
    

    # ITERATE THROUGH ROWS IN DF (EACH HOUR OF DATA)
    for idx in range(len(df)):

        # extract PV and load data from df
        PV_production_kWh = df.loc[idx, 'Production (kW)'] * PV_scaling_factor * num_hrs
        load_kWh = df.loc[idx, 'Load kW'] * num_hrs

        # calculate current annual cost (diesel only)
        curr_d_cost = get_d_cost('prime', load_kWh, num_hrs)[0]                        # current system fulfills entire load with only diesel, with generators in prime fuel consump bc gensets = only source of power
        curr_annualcost = curr_annualcost + curr_d_cost

        # sums total energy produced from PV
        if PV_production_kWh > 0:
            PV_kWh = PV_kWh + PV_production_kWh

        # excess energy produced by PV
        if PV_production_kWh >= load_kWh:                                       
            excessload_kWh = PV_production_kWh - load_kWh
            if bess_kWh_stored < bess_energy:                                           # PV production + battery storage can't be greater than battery bank size
                if excessload_kWh <= bess_power:    charge_kW = excessload_kWh                                  # check that the energy added to the battery storage is less than the BESS power
                if excessload_kWh > bess_power:   charge_kW = bess_power                                      # if the excess energy produced exceeds BESS power, the difference is lost
                
                bess_storage_remaining = bess_energy - bess_kWh_stored
                if bess_storage_remaining < charge_kW:  bess_kWh_stored = bess_energy
                else:   bess_kWh_stored = bess_kWh_stored + charge_kW


        # energy produced by PV does not meet energy need --> batteries or gensets must be used
        if PV_production_kWh < load_kWh:                                        
            remainingload_kWh = load_kWh - PV_production_kWh

            # if remaining load can be supplied by battery only
            if remainingload_kWh <= (bess_efficiency * bess_kWh_stored):
                # if remaining load <= bess power --> bess only
                if remainingload_kWh <= bess_power:                                  # check that the kW discharged from battery to supply load will not exceed BESS power
                    discharge_kW = remainingload_kWh
                    bess_kWh_stored = (bess_efficiency * bess_kWh_stored) - discharge_kW

                # if remaining load > bess power --> bess + gensets
                elif remainingload_kWh > bess_power:                                          # the kW discharged from battery cannot exceed BESS power
                    discharge_kW = bess_power                                               # only the amount of the BESS power can be discharged
                    bess_kWh_stored = (bess_efficiency * bess_kWh_stored) - discharge_kW     # update battery storage to reflect kW discharged
                    
                    # the remaining load must be supplied by gensets
                    d_kWh_need = remainingload_kWh - discharge_kW                           # energy (kWh) that diesel must supply
                    array = get_d_cost('standby', d_kWh_need, num_hrs)               # diesel cost for this timeframe
                    d_cost = array[0]
                    genset_annualcost = genset_annualcost + d_cost                   # add to total diesel cost

                    num_gensets = array[1]
                    if num_gensets_used < num_gensets:
                        num_gensets_used = num_gensets


            # if remaining load cannot be supplied by BESS alone
            elif remainingload_kWh > (bess_kWh_stored * bess_efficiency):               # battery insufficient, gensets needed
                                
                # if bess_kWh_stored < bess_power --> bess_kWh_stored supplies load, then gensets supply the rest
                if bess_kWh_stored <= bess_power:                             # BESS storage remaining is the amount of kW supplying load
                    
                    d_kWh_need = remainingload_kWh - bess_kWh_stored          # energy (kWh) that diesel must supply
                    array = get_d_cost('standby', d_kWh_need, num_hrs)               # diesel cost for this timeframe
                    d_cost = array[0]
                    genset_annualcost = genset_annualcost + d_cost                   # add to total diesel cost

                    num_gensets = array[1]
                    if num_gensets_used < num_gensets:
                        num_gensets_used = num_gensets

                # if bess_kWh_stored > bess_power --> bess_power supplies load, then gensets supply the rest
                elif bess_kWh_stored <= bess_power:                                  # BESS power is the amount of kW supplying load

                    bess_kWh_stored = (bess_efficiency * bess_kWh_stored) - bess_power

                    d_kWh_need = remainingload_kWh - bess_power                      # energy (kWh) that diesel must supply
                    array = get_d_cost('standby', d_kWh_need, num_hrs)               # diesel cost for this timeframe
                    d_cost = array[0]
                    genset_annualcost = genset_annualcost + d_cost                   # add to total diesel cost

                    num_gensets = array[1]
                    if num_gensets_used < num_gensets:
                        num_gensets_used = num_gensets


    # CALCULATE COSTS
    # annual costs
    # print('current annual diesel cost is ' + str(curr_annualcost))

    PV_annualcost = PV_kWh * PV_LCOE
    # print('annual PV cost is ' + str(PV_annualcost))

    # print('new annual diesel cost is ' + str(genset_annualcost))

    # fixed costs
    bat_fixedcost = (KWH_2HR_BAT_COST * bess_energy) + (BAT_ADDHR_COST * (bess_duration - 2) * bess_energy)    # once in lifetime
    # print('fixed battery cost is ' + str(bat_fixedcost))

    genset_fixedcost = STANDBY_KW * GENSET_COST_PER_KW * num_gensets_used                                                  # every 5 years
    # print('genset standby genset fixed cost = ' + str(genset_fixedcost))

    curr_genset_fixedcost = PRIME_KW * GENSET_COST_PER_KW * CURR_NUM_GENSETS
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
        


###########################################################################################

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



###########################################################################################

main()

