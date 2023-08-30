# this is a python script to regrid the models

import os
import sys
import pandas as pd

def main(model_list, var_name, outgrid_file, variant_label, base_loc):
    i = 1
    for mod_name in model_list:
        # access the model csv file
        df = pd.read_csv(base_loc + '/data/model/' + mod_name + '_' + var_name + '.csv')
        # get the path for the given variant label
        if variant_label in df['variant_label'].to_numpy():
            path = df.where(df['variant_label'] == variant_label).dropna()['path'].to_numpy()[0]
            # regridding
            save_base_location = '/scratch/ob22/as8561/data/regridded_models/'
            save_name = mod_name + '_' + var_name + '_' + variant_label + '/'
            save_location = save_base_location + save_name
            if save_name in os.listdir(save_base_location):
                print(f'Finished {i}/{len(model_list)} : {mod_name} -> folder already present')
                i += 1
            else:
                os.system('mkdir -p ' + save_location)
                os.system('./remap ' + path + ' ' + save_location + ' ' + outgrid_file)
                print(f'Finished {i}/{len(model_list)} : {mod_name} -> Variant found and saved')
                i += 1
        else:
            print(f'Finished {i}/{len(model_list)} : {mod_name} -> Variant not found')
            i += 1
    print('Completed all models')

if __name__ == "__main__":
    # model_list = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'AWI-CM-1-1-MR', 'BCC-CSM2-MR', 'BCC-ESM1', 'CESM2-WACCM', 'CESM2', 'CIESM', 'CMCC-CM2-SR5', 'CanESM5', 'E3SM-1-1', 'EC-Earth3-Veg-LR', 'EC-Earth3-Veg', 'EC-Earth3', 'FGOALS-f3-L', 'FGOALS-g3', 'FIO-ESM-2-0', 'GFDL-CM4', 'GFDL-ESM4', 'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'INM-CM4-8', 'INM-CM5-0', 'IPSL-CM6A-LR', 'KACE-1-0-G', 'MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'NESM3', 'NorESM2-LM', 'NorESM2-MM', 'TaiESM1', 'UKESM1-0-LL']
    model_list = ['CNRM-CM6-1', 'CNRM-CM6-1-HR', 'CNRM-ESM2-1', 'MIROC-ES2L', 'UKESM1-0-LL']
    var_name = 'tos'
    outgrid = './outgrid_sst.txt'
    variant_label = 'r1i1p1f2'
    base_loc = sys.argv[1]
    main(model_list, var_name, outgrid, variant_label, base_loc)
