import pandas as pd
import numpy as np
from ggseg import *
import matplotlib.pyplot as plt

pathology = ['EC_CS_DGTAU', 'BRAAK06', 'ABETA', 'CERAD', 'EC_CS_DGNEURONLOSS']
#pathology = ['EC_CS_DGTDP43', 'EC_CS_DGASYN']

for x_var in pathology:
        print(x_var)
        colmns_names = ['roi_label', 'N subjs', 'rho', 'CI', 'p-value', 'p-corr']
        df = pd.read_csv('/Users/pulkit/Desktop/MLCN_2024/invivo_roi_results/' + x_var + 'eTIV_invivo.csv',
                        header=None, names=colmns_names)
        
        print(df['roi_label'])

        df['roi_label_rho'] = df['roi_label'].str.slice(3, -17) + '_left'
        print(df['roi_label_rho'] )
        df['roi_label_p_val'] = df['roi_label'].str.slice(3, -17) + '_right'

        data1 = dict(zip(df['roi_label_rho'], df['rho']))
        plot_dk(data1, cmap='PRGn', figsize=(10,10),
                background='w', edgecolor='k', bordercolor='gray', fontsize=25,
                ylabel='', title='Correlation with ' + x_var)
                
        plt.savefig('/Users/pulkit/Desktop/MLCN_2024/invivo_roi_results/' + x_var + '_mlcn_plots_corr_rescaled.png', bbox_inches='tight', dpi=300)
