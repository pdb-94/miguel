import datetime as dt
import sys
from environment import Environment
from operation import Operator
from evaluation import Evaluation
from report.report import Report


def demonstration(grid_connection=True):
    """
    Create an Off grid system with the following system components
        - PV: 60 kWp
        - Diesel generator: 30 kW
        - Battery storage: 10 kW/30kWh
    :return: environment
    """
    if grid_connection:
        name = 'Grid connected system'
    else:
        name = 'Off grid system NO STORAGE'
    # Add parameters to create environment
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
    # Add load profile from csv-file
    environment.add_load(load_profile=sys.path[1] + '/data/St. Dominics Hospital.csv')
    # Add PV system
    environment.add_pv(p_n=60000,
                       pv_data={'surface_tilt': 20, 'surface_azimuth': 180, 'min_module_power': 250,
                                'max_module_power': 350, 'inverter_power_range': 2500})
    environment.add_wind_turbine(selection_parameters=[3000000, 4000000])
    if grid_connection is False:
        environment.add_diesel_generator(p_n=30000,
                                         fuel_consumption=12,
                                         fuel_price=1.385)
    environment.add_storage(p_n=10000,
                            c=30000,
                            soc=0.25)

    return environment


print('Create environment')
# Off Grid system
env = demonstration(grid_connection=False)
# On Grid system
# env = demonstration(grid_connection=True)

# Run Dispatch
print('Run Dispatch')
operator = Operator(env=env)
evaluation = Evaluation(env=env, operator=operator)
# Create pdf-Report
print('Create report')
report = Report(env=env, operator=operator, evaluation=evaluation)
print('Finished simulation and evaluation.')
