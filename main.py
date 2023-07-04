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
                              location={'latitude': -6.045612,
                                        'longitude': -45.31375,
                                        'terrain': 'Villages, small towns, agricultural buildings with many or high '
                                                   'hedges, woods and very rough and uneven terrain'},
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
                                    'timezone': 'Etc/GMT-4'},
                              economy={'d_rate': 0.03,
                                       'lifetime': 20,
                                       'electricity_price': 0.152,
                                       'diesel_price': 1.06,
                                       'pv_feed_in_tariff': 0,
                                       'wt_feed_in_tariff': 0,
                                       'co2_price': 0,
                                       'currency': 'US$'},
                              ecology={'co2_diesel': 0.2665,
                                       'co2_grid': 0.098},
                              grid_connection=grid_connection,
                              feed_in=False,
                              blackout=False,
                              blackout_data=None,
                              csv_decimal=',',
                              csv_sep=';')
    # Add load profile from csv-file
    environment.add_load(annual_consumption=150000, ref_profile='L0')  # kWh
    # Add PV system
    environment.add_pv(p_n=30000,
                       pv_data={'surface_tilt': 20, 'surface_azimuth': 90, 'min_module_power': 300,
                                'max_module_power': 400, 'inverter_power_range': 2500})
    environment.add_pv(p_n=30000,
                       pv_data={'surface_tilt': 20, 'surface_azimuth': 270, 'min_module_power': 300,
                                'max_module_power': 400, 'inverter_power_range': 2500})
    # environment.add_pv(pv_data={'surface_tilt': 20, 'surface_azimuth': 0, 'pv_module': 'ET_Solar_Industry_ET_M672320WW',
    #                             'inverter': 'SMA_America__STP_62_US_41__480V_', 'modules_per_string': 94.0,
    #                             'strings_per_inverter': 2})
    # Add Windturbine
    # environment.add_wind_turbine(selection_parameters=[3000000, 4000000])
    # environment.add_wind_turbine(turbine_data={'turbine_type': 'E-115/3200', 'hub_height': 92.0, 'p_n': 3200000})
    if not grid_connection:
        environment.add_diesel_generator(p_n=35000,
                                         fuel_consumption=13.5)
    environment.add_storage(p_n=10000,
                            c=30000,
                            soc=0.25)

    return environment


start = dt.datetime.today()
print('Create environment')
# Off Grid system
env = demonstration(grid_connection=False)
# On Grid system
# env = demonstration(grid_connection=True)
# Run Dispatch
print(f'Run Dispatch {dt.datetime.today() - start}')
operator = Operator(env=env)
print(f'Dispatch completed {dt.datetime.today() - start}')
evaluation = Evaluation(env=env, operator=operator)
# Create pdf-Report
print(f'Create report {dt.datetime.today() - start}')
report = Report(env=env, operator=operator, evaluation=evaluation)
print(f'Finished simulation and evaluation {dt.datetime.today() - start}')
