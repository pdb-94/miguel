
import datetime as dt
import pandas as pd
from pathlib import Path
from environment import Environment
from operation import Operator
from evaluation import Evaluation
import os

def demonstration(grid_connection=False, n_modul=None):
    """

    """
    if grid_connection:
        name = 'Grid connected system'
    else:
        name = 'Off grid system'

    # Add parameters to create environment
    environment = Environment(name="Caiambé-Tefé AM",
                              location={'latitude': -3.532906,
                                        'longitude': -64.410861,
                                        'terrain': 'Villages, small towns, agricultural buildings with many or high '
                                                   'hedges, woods and very rough and uneven terrain'},
                              time={'start': dt.datetime(year=2024,
                                                         month=1,
                                                         day=1,
                                                         hour=0,
                                                         minute=0),
                                    'end': dt.datetime(year=2024,
                                                       month=12,
                                                       day=30,
                                                       hour=23,
                                                       minute=59),
                                    'step': dt.timedelta(hours=1),
                                    'timezone': 'Etc/GMT-4'},
                              economy={'d_rate': 0.03,
                                       'lifetime': 20,
                                       'electricity_price': 0.152,
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



    # 1. read csv file/import data
    df = pd.read_csv("Caiambe-Data.csv", sep=";", decimal=",", index_col=0)

    # 2. Index change in datetime
    df.index = pd.to_datetime(df.index, dayfirst=True)
    df = df.iloc[:200]  # short to 200 hours for testing

  
    environment.add_load(load_profile="Caiambe-Data-neu.csv")

    #Num_module = math.ceil(cap_pv / 100)

    for pv in range (n_modul):
        environment.add_pv(p_n=100000, pv_profile=df["PV [W]"],
                           pv_data={'surface_tilt': 20, 'surface_azimuth': 90, 'min_module_power': 300,
                                    'max_module_power': 400, 'inverter_power_range': 2500})

    if not grid_connection:
        environment.add_storage(p_n=550_000,
                                c=85_0000,
                                soc=0.25)
        # **import hydrogen components**
        # electrolyser with p_n power [W]
        environment.add_electrolyser(p_n=1350_000,
                                     c_op_main_n= 21.16,
                                     c_invest_n=2115.19,
                                     lifetime=20)
        # hydrogen storage, capacity [kg]
        environment.add_H2_Storage(capacity=500,
                                   initial_level=0.05,
                                   c_invest_n=610.10,
                                   c_op_main_n=0
                                   )
        # fuel cell, maximum power [W]
        environment.add_fuel_cell(max_power=550_000,
                                  c_invest_n=3421.53,
                                  c_op_main_n=0,
                                  lifetime=10)

    return environment



env = demonstration(grid_connection=False, n_modul=35)
operator = Operator(env=env)
evaluation = Evaluation(env=env, operator=operator)

lcoe = evaluation.evaluation_df.loc['System', 'LCOE [US$/kWh]']
co2 = evaluation.evaluation_df.loc['System', 'Lifetime CO2 emissions [t]']
H2_Anteil = (
    evaluation.evaluation_df.loc['FuelCell_1', 'Annual energy supply [kWh/a]']
    / evaluation.evaluation_df.loc['System', 'Annual energy supply [kWh/a]']
) * 100

p_res = operator.df['P_Res [W]'].sum() / 1_000_000
total = operator.df['Load [W]'].sum() / 1_000_000
coverage = round((1 - p_res / total) * 100, 2)
print(
    "LCOE:",lcoe,
    "CO2 Emissionen:", co2,
    "Wasserstoffnutzung:", H2_Anteil

)
