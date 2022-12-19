import matplotlib.pyplot as plt
import pandas as pd
import pvlib

tmy = pd.read_csv('pv_gis_akwatia.csv', skiprows=16, nrows=8760,
                  usecols=['time(UTC)', 'T2m', 'G(h)', 'Gb(n)', 'Gd(h)', 'WS10m'],
                  index_col=0)
# tmy.index = pd.to_datetime(tmy.index, format='%Y%m%d:%H%M')
tmy.index = pd.date_range(start='2022-01-01 00:00', end='2022-12-31 23:00', freq='1h')
tmy.columns = ['temp_air', 'ghi', 'gni', 'dhi', 'wind_speed']

tmy.to_csv('pvlib_weather_data.csv')

data, months_selected, inputs, metadata = pvlib.iotools.get_pvgis_tmy(latitude=50.0, longitude=7.0,
                                                                      startyear=2005, endyear=2016,
                                                                      outputformat='json', usehorizon=True,
                                                                      userhorizon=None, map_variables=True, timeout=30,
                                                                      url='https://re.jrc.ec.europa.eu/api/')
print(data)
print(data.columns)
# print(inputs)
# print(metadata)
# tmy.plot()
# plt.show()
