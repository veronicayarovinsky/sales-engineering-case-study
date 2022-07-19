# plotresults.py - plot results.csv file as a heatmap

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os


MAIN_PATH = os.getcwd()
PROJECTDATA_PATH = MAIN_PATH + '/ProjectData'

os.chdir(PROJECTDATA_PATH)

file = 'results_step3.csv'
# file = 'results_step2.csv'
df = pd.read_csv(file, index_col = 0)
df = (df/1000000)

plt.imshow( df , cmap = 'autumn' , interpolation = 'nearest' )
plt.title( "Net Savings after 20 years" )
# note: the axes ticks are not labeled properly

# Plot a colorbar with label.
cb = plt.colorbar()
cb.set_label('Net Savings, in millions')

plt.xlabel('PV System (kW)')
plt.ylabel('Battery Storage (kWh)')

plt.show()
