# sales-engineering-case-study

## Case Study:
A remote island in the Pacific has a load profile as described in first tab of the attached excel file. The island is currently powered by 3 Cummins DSGAC-150 gensets (datasheet in the excel file). The customer is sourcing diesel at $1/L and has to purchase new gensets every 5yrs at a cost of $0.4/W. A project developer wants to add PV and storage to offset a portion of, if not the entire, diesel usage. The attached document also contains PV production for a 100kW PV system but it may be scaled up or down as necessary. PV LCOE on this island is 5c/kWh. Installed battery costs start at $500/kWh for a 2hr system with a $25/kWh addition for every additional hour of storage required.
 
What is the most optimal solution for customer? 


## Files:
* `model.py` contains the model to solve the case study, with results saved to `results.csv`
* `plotresults.py` graphs results from model.py

* Data Provided by Case Study (in ProjectData directory):
    * load.csv
    * PV_data.csv

* OrganizingData directory contains python files to sort and organize data. It contains the following files:
    * `avgPVhourly.py` averages the 5-min interval data from `PV_data.csv` by hour, saved to `PV_data_hourly.csv`
    * `avgPVdaily.py` averages the PV data from `PV_data.csv` for each day, saved to `PV_dailyavg.csv`
    * `avgloaddaily.py` averages the load data from `load.csv` for each day, saved to `load.csv`
    * `avgbyhour.py` averages data for each hour separately to create a daily profile for both PV and load data, saved to `PV_dailyprofile.csv` and `load_dailyprofile.csv`.
    * `combinedata.py` compiles hourly PV data and hourly load data into `hourlydata.csv` to be used by `model.py`


