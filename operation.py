import time
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt

# MiGUEL modules
import pandas as pd

import environment as en
from pv import PV
from windturbine import WindTurbine
from report.report import Report


# TODO:
#   - Develop dispatch strategies
#   - Research optimization algorithm python
#   - Optimize:
#       - PV/WT size
#       - Energy storage Y/N
#       - Energy Storage for peak shaving to use smaller Generator
#       - Generator type


class Operator:
    """
    Class to control environment, run dispatch and parameter optimization
    """

    def __init__(self,
                 env: en.Environment):
        """
        :param env:
        """
        self.env = env
        self.energy_data = self.env.calc_energy_consumption_parameters()
        self.energy_consumption = self.energy_data[0]
        self.peak_load = self.energy_data[1]
        self.system = {0: 'Off Grid System', 1: 'Stable Grid connection', 2: 'Unstable Grid connection'}
        self.df = self.build_df()
        self.run()

    def build_df(self):
        """
        Assign columns to pd.DataFrame
        :return: pd.DataFrame
            DataFrame with component columns
        """
        df = pd.DataFrame(columns=['Load [W]', 'P_Res [W]'], index=self.env.time)
        df['Load [W]'] = self.env.df['P_Res [W]']
        df['P_Res [W]'] = self.env.df['P_Res [W]']
        if self.env.blackout is True:
            df['Blackout'] = self.env.df['Blackout']
        for pv in self.env.pv:
            pv_col = pv.name + ' [W]'
            df[pv_col] = 0
            df[pv.name + ' production [W]'] = pv.df['P [W]']
        for wt in self.env.wind_turbine:
            wt_col = wt.name + ' [W]'
            df[wt_col] = 0
            df[wt.name + ' production [W]'] = wt.df['P [W]']
        for es in self.env.storage:
            es_col = es.name + ' [W]'
            df[es_col] = 0
        for grid in self.env.grid:
            grid_col = grid.name + ' [W]'
            df[grid_col] = 0
        for dg in self.env.diesel_generator:
            dg_col = dg.name + ' [W]'
            df[dg_col] = 0

        return df

    def run(self):
        """
        run dispatch:
        Component priorities for On Grid Systems:
            1) RE self-consumption
            2) Charge storage from RE
            Stable grid connection:
                3) Cover residual load from Storage
                4) Cover residual load from Grid
            Unstable Grid connection:
                No Blackout:
                    3) Cover residual load from Grid
                Blackout:
                    4.1) Cover load from Storage
                    4.2) Cover load from Diesel Generator
        Component priorities for of Grid systems:
            1) RE self consumption
            2) Charge storage from RE
            3) Cover load from Storage
            4) Cover load from Diesel Generator

        :return: None
        """
        env = self.env
        if env.grid_connection is True:
            if env.blackout is True:
                system = self.system[2]
            else:
                system = self.system[1]
        else:
            system = self.system[0]
        # Time step iteration
        for clock in self.df.index:
            for component in env.re_supply:
                # Priority 1: RE self supply
                self.re_self_supply(clock=clock, component=component)
                # Priority 2: Charge Storage from RE
                for es in env.storage:
                    self.re_charge(clock=clock, es=es, component=component)
            if env.grid_connection is True:
                if env.blackout is True:
                    # System: Unstable grid connection
                    if env.df.loc[clock, 'Blackout'] is False:
                        # No Blackout: Priority 3 cover load from grid
                        self.grid_profile(clock=clock)
                    else:
                        # Blackout: Priority 3 cover load from storage
                        # TODO: Integrate low_load_behavior here??
                        #  --> if low_load_behavior is False different Priorities (same for off Grid system)
                        #
                        for es in env.storage:
                            if self.df.loc[clock, 'P_Res [W]'] > 0:
                                power = self.df.loc[clock, 'P_Res [W]']
                                discharge_power = es.discharge(clock=clock, power=power)
                                self.df.loc[clock, es.name + ' [W]'] += discharge_power
                                self.df.loc[clock, 'P_Res [W]'] += discharge_power
                        # Priority 4 cover load with diesel generator
                        for dg in env.diesel_generator:
                            if self.df.loc[clock, 'P_Res [W]'] > 0:
                                self.dg_profile(clock=clock, dg=dg)
                else:
                    # System: Stable grid connection
                    # Priority 3: Cover load from storage
                    for es in env.storage:
                        if self.df.loc[clock, 'P_Res [W]'] > 0:
                            power = self.df.loc[clock, 'P_Res [W]']
                            discharge_power = es.discharge(clock=clock, power=power)
                            self.df.loc[clock, es.name + ' [W]'] += discharge_power
                            self.df.loc[clock, 'P_Res [W]'] += discharge_power
                    # Priority 4: Cover load from grid
                    self.grid_profile(clock=clock)
            else:
                # System: Off grid system
                for es in env.storage:
                    if self.df.loc[clock, 'P_Res [W]'] > 0:
                        power = self.df.loc[clock, 'P_Res [W]']
                        discharge_power = es.discharge(clock=clock, power=power)
                        self.df.loc[clock, es.name + ' [W]'] += discharge_power
                        self.df.loc[clock, 'P_Res [W]'] += discharge_power
                for dg in env.diesel_generator:
                    if self.df.loc[clock, 'P_Res [W]'] > 0:
                        self.dg_profile(clock=clock, dg=dg)

    def re_self_supply(self, clock: dt.datetime, component: object):
        """
        Calculate re self-consumption
        :param clock: dt.datetime
             time stamp
        :param component: object
            re component (pv, wind turbine)
        :return: None
        """
        df = self.df
        df.loc[clock, component.name + ' [W]'] = np.where(df.loc[clock, 'P_Res [W]'] > component.df.loc[clock, 'P [W]'],
                                                          component.df.loc[clock, 'P [W]'], df.loc[clock, 'P_Res [W]'])
        df.loc[clock, component.name + ' [W]'] = np.where(df.loc[clock, component.name + ' [W]'] < 0, 0,
                                                          df.loc[clock, component.name + ' [W]'])
        df.loc[clock, component.name + ' remain [W]'] = np.where(
            component.df.loc[clock, 'P [W]'] - df.loc[clock, 'P_Res [W]'] < 0,
            0, component.df.loc[clock, 'P [W]'] - df.loc[clock, 'P_Res [W]'])
        df.loc[clock, 'P_Res [W]'] -= df.loc[clock, component.name + ' [W]']

    def re_charge(self, clock: dt.datetime, es: object, component: object):
        """
        Charge energy storage from renewable pv, wind turbine
        :param clock: dt.datetime
            time stamp
        :param es: object
            energy storage
        :param component: object
            re component (pv, wind turbine)
        :return: None
        """
        env = self.env
        index = env.re_supply.index(component)
        if clock == self.df.index[0]:
            if index == 0:
                # Set values for first time step
                es.df.loc[clock, 'P [W]'] = 0
                es.df.loc[clock, 'SOC'] = es.soc
                es.df.loc[clock, 'Q [Wh]'] = es.soc * es.c
        # Charge storage
        charge_power = es.charge(clock=clock,
                                 power=self.df.loc[clock, component.name + ' remain [W]'])
        self.df.loc[clock, es.name + ' [W]'] += es.df.loc[clock, 'P [W]']
        self.df.loc[clock, component.name + ' remain [W]'] -= charge_power

    def grid_profile(self, clock: dt.datetime):
        """
        Cover load from power grid
        :param clock: dt.datetime
            time stamp
        :return: None
        """
        df = self.df
        grid = self.env.grid[0].name
        df.loc[clock, grid + ' [W]'] = self.df.loc[clock, 'P_Res [W]']
        df.loc[clock, 'P_Res [W]'] = 0

    def dg_profile(self, clock: dt.datetime, dg: object):
        """

        :return: None
        """
        if dg.low_load_behavior is True:
            power = self.df.loc[clock, 'P_Res [W]']
            dg.low_load_model(clock=clock, power=power)
        else:
            print('Buy a f***ing new generator.')


if __name__ == '__main__':
    start_time = time.time()
    start = dt.datetime(year=2021, month=1, day=1, hour=0, minute=0)
    end = dt.datetime(year=2021, month=1, day=1, hour=23, minute=59)
    environment = en.Environment(name='St. Dominics Hospital',
                                 time={'start': start, 'end': end, 'step': dt.timedelta(minutes=15), 'timezone': 'CET'},
                                 location={'longitude': -0.7983,
                                           'latitude': 6.0442,
                                           'altitude': 50,
                                           'roughness_length': 'Open terrain with smooth surface, e.g., concrete, airport runways, mowed grass'},
                                 grid_connection=True, blackout=False)
    load_profile = 'C:/Users/Rummeny/PycharmProjects/MiGUEL_Fulltime/data/load/St. Dominics Hospital.csv'
    environment.add_load(load_profile=load_profile)
    environment.add_pv(p_n=65000,
                       pv_data={'surface_tilt': 20, 'surface_azimuth': 180, 'min_module_power': 250,
                                'max_module_power': 350, 'inverter_power_range': 65000})
    environment.add_pv(p_n=25000,
                       pv_data={'surface_tilt': 20, 'surface_azimuth': 180, 'min_module_power': 250,
                                'max_module_power': 350, 'inverter_power_range': 25000})

    environment.add_grid()
    # environment.add_wind_turbine(p_n=4200000, turbine_data={"turbine_type": "E-126/4200", "hub_height": 135})
    environment.add_diesel_generator(p_n=10000, fuel_consumption=9.7, fuel_price=1.20, low_load_behavior=True)
    environment.add_storage(p_n=5000, c=50000, soc=0.5)
    operator = Operator(env=environment)
    # print(operator.df)
    # operator.df.to_csv('env.csv')
    # operator.df.plot()
    # plt.show()
    report = Report(environment=environment, operator=operator)
    print('Runtime: %s seconds' % (time.time() - start_time))
