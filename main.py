import datetime as dt
from environment import Environment
from operation import Operator
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

