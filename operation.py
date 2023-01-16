import time
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt

# MiGUEL modules
import pandas as pd

import environment as en
from report.report import Report


# TODO:
#   - Develop dispatch strategies
#   - Research optimization algorithm python


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
        self.df = self.build_df()
        self.run()

    def build_df(self):
        """
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
        for wt in self.env.wind_turbine:
            wt_col = wt.name + ' [W]'
            df[wt_col] = 0
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
        run dispatch
        :return: None
        """
        env = self.env
        if env.grid_connection is True:
            if env.blackout is True:
                """
                Priorities for on grid system with Blackouts:
                1) RE self consumption
                2) Charge storage from RE
                3) Cover Residual load from Grid
                4) If Blackout:
                    4.1) Cover load from Storage
                    4.2) Cover load from Diesel Generator
                """
                print('Grid connection with blackouts')
                # Priority 1: RE supply
                for pv in env.pv:
                    self.pv_profile(pv=pv)
                    # Priority 2 charge storage
                    for es in env.storage:
                        for clock in self.df.index:
                            charging_power = es.charge(clock=clock, power=self.df.loc[clock, pv.name + ' remain [W]'])
                            self.df.loc[clock, es.name + ' [W]'] = es.df.loc[clock, 'P [W]']
                            self.df.loc[clock, pv.name + ' remain [W]'] -= charging_power
                            # print(clock, self.df.loc[clock, es.name + ' [W]'], es.df.loc[clock, 'Q [Wh]'])
                # Priority 1: RE supply
                for wt in env.wind_turbine:
                    self.wt_profile(wt=wt)
                    # Priority 2 charge storage
                    for es in env.storage:
                        for clock in self.df.index:
                            charging_power = es.charge(clock=clock, power=self.df.loc[clock, wt.name + ' remain [W]'])
                            self.df.loc[clock, es.name + ' [W]'] = es.df.loc[clock, 'P [W]']
                            self.df.loc[clock, wt.name + ' remain [W]'] -= charging_power
            else:
                print('Grid connection without blackouts')
                # Priority 1: RE supply
                for pv in env.pv:
                    self.pv_profile(pv=pv)
                    # Priority 2 charge storage
                    for es in env.storage:
                        for clock in self.df.index:
                            charging_power = es.charge(clock=clock, power=self.df.loc[clock, pv.name + ' remain [W]'])
                            self.df.loc[clock, es.name + ' [W]'] = es.df.loc[clock, 'P [W]']
                            self.df.loc[clock, pv.name + ' remain [W]'] -= charging_power
                            # print(clock, self.df.loc[clock, es.name + ' [W]'], es.df.loc[clock, 'Q [Wh]'])
                # Priority 1: RE supply
                for wt in env.wind_turbine:
                    self.wt_profile(wt=wt)
                    # Priority 2 charge storage
                    for es in env.storage:
                        for clock in self.df.index:
                            charging_power = es.charge(clock=clock, power=self.df.loc[clock, wt.name + ' remain [W]'])
                            self.df.loc[clock, es.name + ' [W]'] = es.df.loc[clock, 'P [W]']
                            self.df.loc[clock, wt.name + ' remain [W]'] -= charging_power
        else:
            print('Off Grid system')

    def pv_profile(self, pv):
        """

        :return:
        """
        self.df[pv.name + ' [W]'] = np.where(self.df['P_Res [W]'] > pv.df['P [W]'], pv.df['P [W]'], self.df['P_Res [W]'])
        self.df[pv.name + ' [W]'] = np.where(self.df[pv.name + ' [W]'] < 0, 0, self.df[pv.name + ' [W]'])
        self.df[pv.name + ' remain [W]'] = np.where(pv.df['P [W]'] - self.df['P_Res [W]'] < 0, 0, pv.df['P [W]'] - self.df['P_Res [W]'])
        self.df['P_Res [W]'] -= self.df[pv.name + ' [W]']

    def wt_profile(self, wt):
        self.df[wt.name + ' [W]'] = np.where(self.df['P_Res [W]'] > wt.df['P [W]'], wt.df['P [W]'], self.df['P_Res [W]'])
        self.df[wt.name + ' [W]'] = np.where(self.df[wt.name + ' [W]'] < 0, 0, self.df[wt.name + ' [W]'])
        self.df[wt.name + ' remain [W]'] = np.where(wt.df['P [W]'] - self.df['P_Res [W]'] < 0, 0, wt.df['P [W]'] - self.df['P_Res [W]'])
        self.df['P_Res [W]'] -= self.df[wt.name + ' [W]']

    def es_profile(self):
        """

        :return:
        """

    def grid_profile(self):
        """

        :return:
        """

    def dg_profile(self):
        """

        :return:
        """

    # def dispatch_3(self):
    #     """
    #     dispatch strategy 3:
    #         Components: PV-System, Wind Turbine, Load, Diesel Generator
    #         - Off grid system
    #         - max. PV/WT self-consumption
    #         - Curtail remaining PV/WT production
    #         - Cover remaining load with Diesel Generator
    #     :return: None
    #     """
    #     env = self.env
    #     # Calculate PV Curtailment
    #     env.df['PV Curtail [W]'] = 0
    #     pv_curtail = env.df['P_Res [W]'] - env.df['PV total power [W]']
    #     env.df['PV Curtail [W]'] = np.where(pv_curtail > 0, 0, pv_curtail)
    #     # Calculate WT Curtailment
    #     env.df['WT Curtail [W]'] = 0
    #     wt_curtail = env.df['P_Res [W]'] - env.df['WT total power [W]']
    #     env.df['WT Curtail [W]'] = np.where(wt_curtail > 0, 0, wt_curtail)
    #     env.calc_self_supply()
    #     # Run generator model
    #     for generator in env.diesel_generator:
    #         generator.run()
    #         env.df[generator.name + ': P [W]'] = generator.df['P [W]'].values
    #     # Calculate RE load
    #     re_load_adjusted = env.df['P_Res [W]'] - env.df['DG_1: P [W]']
    #     env.df['RE self consumption [W]'] = np.where(re_load_adjusted > env.df['Self supply [W]'],
    #                                                  env.df['Self supply [W]'],
    #                                                  re_load_adjusted)
    #     env.df['RE Curtailment adjusted [W]'] = -(env.df['Self supply [W]'] - env.df['RE self consumption [W]'])

    # def system_comparison(self, component: str = None):
    #     """
    #     TODO: Compare system components, single components and all components. Optimization based on levelized cost of energy
    #         - PV/WT plant size
    #         - Diesel generator model (Standard)
    #         - ES Y/N (size)
    #         - Problem:
    #             - all components influence each other (recursive behavior)
    #
    #     :param component: str
    #         system component to compare
    #     :return: None
    #     """
    #     if component == 'Diesel Generator':
    #         print('Compare Diesel Generator with Generator Model.')
    #     elif component == 'PV':
    #         print('Compare PV plant size +-20%.')
    #     elif component == 'WT':
    #         print('Compare System')


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
                                 grid_connection=True)
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
    environment.add_diesel_generator(p_n=10000, fuel_consumption=9.7, fuel_price=1.20, low_load_behavior=False)
    environment.add_storage(p_n=5000, c=50000, soc=0.5)
    operator = Operator(env=environment)
    print(operator.df)
    # print(operator.df.columns)
    operator.df.plot()
    plt.show()
    operator.df.to_csv('env.csv')
    # report = Report(environment=environment, operator=operator)
    print('Runtime: %s seconds' % (time.time() - start_time))
