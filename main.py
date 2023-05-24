import datetime as dt

import pandas as pd

from environment import Environment
from operation import Operator
from evaluation import Evaluation
from report.report import Report

"""
PROGRAM DESCRIPTION

1) Setup classes
    1.1) Create instance of class Environment with input parameters:
        - name: str (Project Name)
        - time: dict {start: dt.datetime, end: dt.datetime, step: dt.timedelta} (period under review)
        - economy: dict {d_rate (discount rate): float, lifetime (project lifetime): int, electricity_price: float,
                         co2_price: float, pv_feed_in_tariff: float, wt_feed_in_tariff: float, currency: str}
        - ecology: dict {co2_diesel (co2-emissions kg/kWh): float, co2_grid (co2-emissions kg/kWh): float}
        - location: dict {longitude: float, latitude: float, altitude: float, terrain: str)
            - terrain:  ['Water surfaces', 
                         'Open terrain with smooth surface, e.g., concrete, airport runways, mowed grass',
                         'Open agricultural terrain without fences or hedges, possibly with widely scattered houses, very rolling hills',
                         'Agricultural terrain with some houses and 8 meter high hedges at a distance of approx. 1250 meters',
                         'Agricultural terrain with many houses, bushes, plants or 8 meter high hedges at a distance of approx. 250 meters',
                         'Villages, small towns, agricultural buildings with many or high hedges, woods and very rough and uneven terrain',
                         'Larger cities with tall buildings', 'Large cities, tall buildings, skyscrapers']
                         
    DISCLAIMER: to enable off line use. The weather data needs to be imported. The style of the csv input file is the same style the weather data gets exported.
                         
    1.2) Add system components of energy system to Environment:
        - PV: environment.add_pv() --> Check function for parameters
        - Wind turbine: environment.add_wind_turbine() --> Check function for parameters
        - Grid: environment.add_grid() --> Check function for parameters
        - Diesel generator: environment.add_diesel_generator() --> Check function for parameters
        - Battery storage: environment.add_storage() --> Check function for parameters
        - Load: environment.add_load() --> Check function for parameters
    
    1.3) Create instance of class Operator with input parameter:
        - env: instance of class Environment
    
    1.4) Create instance of class Report with input parameters:
        - env: instance of class Environment
        - operator: instance of class Operator

2) Run program
    2.1) Environment creates...
        ... time frame
        ... location
        ... weather data
        ... system components
    2.2) Operator ...
        ... runs dispatch
        ... controls dispatch
        ... evaluates system
        ... returns data
    2.3) Report ...
        ... create report with all relevant output
"""


def demonstration(grid_connection=True):
    """
    Create an Off grid system with the following system components
        - PV: 60 kWp
        - Diesel generator: 30 kW
        - Battery storage: 10 kW/30kWh
    :return: environemnt
    """
    if grid_connection:
        name = 'Grid connected system'
    else:
        name = 'Off grid system'
    environment = Environment(name=name,
                              location={'longitude': -0.7983,
                                        'latitude': 6.0442,
                                        'altitude': 20,
                                        'terrain': 'Agricultural terrain with many houses, bushes, plants or 8 meter high hedges '
                                                   'at a distance of approx. 250 meters'},
                              time={'start': dt.datetime(year=2022,
                                                         month=1,
                                                         day=1,
                                                         hour=0,
                                                         minute=0),
                                    'end': dt.datetime(year=2022,
                                                       month=12,
                                                       day=31,
                                                       hour=23,
                                                       minute=59),
                                    'step': dt.timedelta(minutes=15),
                                    'timezone': 'GMT'},
                              economy={'d_rate': 0.03,
                                       'lifetime': 20,
                                       'electricity_price': 0.14,
                                       'diesel_price': 1.385,
                                       'pv_feed_in_tariff': 0,
                                       'wt_feed_in_tariff': 0,
                                       'co2_price': 0,
                                       'currency': 'US$'},
                              ecology={'co2_diesel': 0.2665,
                                       'co2_grid': 0.1350},
                              grid_connection=grid_connection,
                              feed_in=False,
                              blackout=False,
                              blackout_data=None,
                              csv_decimal=',',
                              csv_sep=';')
    environment.add_load(annual_consumption=150000)  # kWh
    environment.add_pv(p_n=60000,
                       pv_data={'surface_tilt': 20, 'surface_azimuth': 180, 'min_module_power': 250,
                                'max_module_power': 350, 'inverter_power_range': 2500})
    if grid_connection is False:
        environment.add_diesel_generator(p_n=10000,
                                         fuel_consumption=11.98,
                                         fuel_price=1.385)
    environment.add_storage(p_n=10000,
                            c=30000,
                            soc=0.25)

    return environment


# Off Grid system
print('Create environment')
env = demonstration(grid_connection=False)
# On Grid system
# env = demonstration(grid_connection=True)

# Run Dispatch
print('Run Dispatch')
operator = Operator(env=env)
# Create pdf-Report
print('Create report')
report = Report(env=env, operator=operator)
print('Finished simulation and evaluation.')
