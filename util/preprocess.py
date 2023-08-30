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
    da_arr[0].to_netcdf(base_loc + mod_name + '/precip.nc')
    da_arr[1].to_netcdf(base_loc + mod_name + '/sst.nc')
    da_arr[2].to_netcdf(base_loc + mod_name + '/nino.nc')
    da_arr[3].to_netcdf(base_loc + mod_name + '/dmi.nc')


def calc_anom(
    input_da,
    base_start_date: str = "1960-01-01",
    base_end_date: str = "1990-01-01",
    start_year: str = "1891-01-01",
    end_year: str = "2015-01-01",
    # var = "Temperature",
    # units = 'K'
):

    # define the base climatology
    base_clim = input_da.sel(time=slice(base_start_date, base_end_date))

    # calculate the monthly climatology for the base years
#     da_clim_coarsen = base_clim.coarsen(time=12)
    da_clim = base_clim.groupby("time.month").mean("time")
    da_anom = input_da.sel(time = slice(start_year, end_year)).groupby("time.month") - da_clim
    
    return da_anom



def preproc(model_list):
    variants_used = ['r1i1p1f1', 'r1i1p1f2']
    for model in model_list:
        try:
            sst = xr.open_mfdataset(f'/g/data/ob22/as8561/data/regridded_models/{model}_tos_{variants_used[0]}/*.nc')#.load()
            precip = xr.open_mfdataset(f'/g/data/ob22/as8561/data/regridded_models/{model}_pr_{variants_used[0]}/*.nc')#.load()
        except OSError:
            sst = xr.open_mfdataset(f'/g/data/ob22/as8561/data/regridded_models/{model}_tos_{variants_used[1]}/*.nc')#.load()
            precip = xr.open_mfdataset(f'/g/data/ob22/as8561/data/regridded_models/{model}_pr_{variants_used[1]}/*.nc')#.load()

        nino_anom = calc_anom(sst.tos).sel(lat = slice(-5, 5), lon = slice(-170, -120)).mean(('lat', 'lon'))
        precip_anom = calc_anom(precip.pr*86400*30).sel(time = slice('1891-01-01', '2015-01-01'))
        sst_anom = calc_anom(sst.tos).sel(time = slice('1891-01-01', '2015-01-01'))
        anom_wio = sst_anom.sel(lat = slice(-10, 10), lon = slice(50, 70)).mean(["lat", "lon"])
        anom_eio = sst_anom.sel(lat = slice(-10, 0), lon = slice(90, 110)).mean(["lat", "lon"])
        dmi = anom_wio - anom_eio

        # detrending
        precip_anom_resid = detrend_separate(precip_anom)
        nino_anom_resid = detrend_separate(nino_anom)
        sst_anom_resid = detrend_separate(sst_anom)
        # load te data into memory
        precip_anom_resid = precip_anom_resid.load()
        nino_anom_resid = nino_anom_resid.load()
        sst_anom_resid = sst_anom_resid.load()
        dmi = dmi.sel(time = slice('1900-01-01', '2015-01-01')).load()
        # rename stuff
        nino_anom_resid.name = 'nino'
        sst_anom_resid.name = 'sst'
        precip_anom_resid.name = 'precip'
        dmi.name = 'dmi'

        # save the data files
        save_files0(model, [precip_anom_resid, sst_anom_resid, nino_anom_resid, dmi])
        print('Completed ' + model)
