import datetime as dt
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
        name = 'Off grid system'
    # Add parameters to create environment
    environment = Environment(name=name,
                              location={'latitude': 6.0442,
                                        'longitude': -0.7983,
                                        'altitude': 100,
                                        'terrain': 'Agricultural terrain with many houses, bushes, plants or 8 meter '
                                                   'high hedges at a distance of approx. 250 meters'},
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
                                    'timezone': 'Etc/GMT'},
                              economy={'d_rate': 0.03,
                                       'lifetime': 20,
                                       'electricity_price': 0.375,
                                       'diesel_price': 1.56,
                                       'pv_feed_in_tariff': 0.07,
                                       'wt_feed_in_tariff': 0.07,
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
    environment.add_load(annual_consumption=150000, ref_profile='L0')  # kWh
    # Add PV system
    environment.add_pv(p_n=60000,
                       pv_data={'surface_tilt': 20, 'surface_azimuth': 0, 'min_module_power': 300,
                                'max_module_power': 400, 'inverter_power_range': 2500})
    environment.add_pv(p_n=30000,
                       pv_data={'surface_tilt': 20, 'surface_azimuth': 270, 'min_module_power': 300,
                                'max_module_power': 400, 'inverter_power_range': 2500})
    # environment.add_wind_turbine(selection_parameters=[3000000, 4000000])
    if not grid_connection:
        environment.add_diesel_generator(p_n=30000,
                                         fuel_consumption=12,
                                         fuel_price=1.385)
    environment.add_storage(p_n=10000,
                            c=30000,
                            soc=0.25)

    return environment


start = dt.datetime.today()
print('Create environment')
# Off Grid system
# env = demonstration(grid_connection=False)
# On Grid system
env = demonstration(grid_connection=True)
# Run Dispatch
print(f'Run Dispatch {dt.datetime.today() - start}')
operator = Operator(env=env)
print(f'Dispatch completed {dt.datetime.today() - start}')
evaluation = Evaluation(env=env, operator=operator)
# Create pdf-Report
print(f'Create report {dt.datetime.today() - start}')
report = Report(env=env, operator=operator, evaluation=evaluation)
print(f'Finished simulation and evaluation {dt.datetime.today() - start}')
