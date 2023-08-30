# Function to preprocess the regridded data


import xarray as xr


def detrend_separate(da, period=9):
    trend = da.rolling(time = period*12).mean('time')
    da_detrend = da - trend
    return da_detrend.sel(time = slice('1900-01-01', '2015-01-01'))


def save_files0(mod_name, da_arr):
    import os
    base_loc = '/scratch/ob22/as8561/data/preproc/'
    os.system('mkdir -p ' + base_loc + mod_name)
    da_arr[0].to_netcdf(base_loc + mod_name + '/base_precip.nc')
    da_arr[1].to_netcdf(base_loc + mod_name + '/base_sst.nc')


def calc_clim(
    input_da,
    base_start_date: str = "1960-01-01",
    base_end_date: str = "1990-01-01",
):

    # define the base climatology
    base_clim = input_da.sel(time=slice(base_start_date, base_end_date))

    # calculate the monthly climatology for the base years
#     da_clim_coarsen = base_clim.coarsen(time=12)
    da_clim = base_clim.groupby("time.month").mean("time")
    
    return da_clim



def preproc_base(model_list):
    variants_used = ['r1i1p1f1', 'r1i1p1f2']
    for model in model_list:
        try:
            sst = xr.open_mfdataset(f'/g/data/ob22/as8561/data/regridded_models/{model}_tos_{variants_used[0]}/*.nc')#.load()
            precip = xr.open_mfdataset(f'/g/data/ob22/as8561/data/regridded_models/{model}_pr_{variants_used[0]}/*.nc')#.load()
        except OSError:
            sst = xr.open_mfdataset(f'/g/data/ob22/as8561/data/regridded_models/{model}_tos_{variants_used[1]}/*.nc')#.load()
            precip = xr.open_mfdataset(f'/g/data/ob22/as8561/data/regridded_models/{model}_pr_{variants_used[1]}/*.nc')#.load()

        precip_clim = calc_clim(precip.pr*86400*30)
        sst_clim = calc_clim(sst.tos)

        # load te data into memory
        precip_clim = precip_clim.load()
        sst_clim = sst_clim.load()

        # save the data files
        save_files0(model, [precip_clim, sst_clim])
        print('Completed ' + model)