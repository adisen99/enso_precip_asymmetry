# Function to preprocess the regridded data of all members of a large ensemble


import xarray as xr
from statsmodels.tsa.seasonal import STL


def detrend1d(arr, period = 9*12):
    res = STL(arr, period = period).fit()
    arr_det = arr - res.trend
    return arr_det

# def detrend_separate(da, period=9):
#     trend = da.rolling(time = period*12).mean('time')
#     da_detrend = da - trend
#     return da_detrend.sel(time = slice('1900-01-01', '2015-01-01'))
def detrend_separate(da, dim):
    return xr.apply_ufunc(detrend1d, da, input_core_dims=[[dim]], output_core_dims=[[dim]])


def save_files0(mod_name, variant, da_arr):
    import os
    # base_loc = '/scratch/ob22/as8561/data/preproc/'
    base_loc = '/g/data/ob22/as8561/data/preproc_files/'
    save_loc = base_loc + mod_name + '/' + variant
    os.system('mkdir -p ' + save_loc)
    os.system('rm -rf ' + save_loc + '/*')
    da_arr[0].to_netcdf(save_loc + '/precip.nc')
    da_arr[1].to_netcdf(save_loc + '/nino.nc')
    da_arr[2].to_netcdf(save_loc + '/dmi.nc')
    da_arr[3].to_netcdf(save_loc + '/threshold.nc')


def calc_anom(
    input_da,
    base_start_date: str = "1960-01-01",
    base_end_date: str = "1990-01-01",
    start_year: str = "1900-01-01",
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
    
    return da_anom, da_clim



def preproc_le(mod_name, variant_list):
    for variant in variant_list:
        sst = xr.open_mfdataset(f'/g/data/ob22/as8561/data/regridded_large_ensemble/{mod_name}_tos_{variant}/*.nc')#.load()
        precip = xr.open_mfdataset(f'/g/data/ob22/as8561/data/regridded_large_ensemble/{mod_name}_pr_{variant}/*.nc')#.load()

        sst_anom, sst_base = calc_anom(sst.tos)
        nino_anom = sst_anom.sel(lat = slice(-5, 5), lon = slice(-170, -120)).mean(('lat', 'lon'))
        anom_wio = sst_anom.sel(lat = slice(-10, 10), lon = slice(50, 70)).mean(["lat", "lon"])
        anom_eio = sst_anom.sel(lat = slice(-10, 0), lon = slice(90, 110)).mean(["lat", "lon"])
        dmi = anom_wio - anom_eio

        # detrending
        # precip_anom_resid = detrend_separate(precip_anom)
        nino34 = detrend_separate(nino_anom.load(), 'time').rolling(time=3).mean('time')
        threshold = nino34.std('time')
        # sst_anom_resid = detrend_separate(sst_anom)
        
        # load the data into memory
        precip_mon = (precip.pr*86400*30).sel(time = slice('1900-01-01', '2015-01-01')).load()
        precip_mon['time'] = nino34['time']
        dmi = dmi.load()
        # rename stuff
        precip_mon.name = 'precip'
        nino34.name = 'nino'
        dmi.name = 'dmi'

        # save the data files
        save_files0(mod_name, variant, [precip_mon, nino34, dmi, threshold])
        print('Completed ' + mod_name + '->' + variant)
