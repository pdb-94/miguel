import sys
import numpy as np
import datetime as dt
import pandas as pd
# MiGUEL modules
from environment import Environment
from components.pv import PV
from components.dieselgenerator import DieselGenerator
from components.windturbine import WindTurbine
from components.storage import Storage
from components.grid import Grid
from lcoe.lcoe import lcoe as py_lcoe


class Operator:
    """
    Class to control environment, dispatch dispatch and parameter optimization
    """

    def __init__(self,
                 env: Environment):
        """
        :param env: env.Environment
            system environment
        """
        self.env = env
        self.energy_data = self.env.calc_energy_consumption_parameters()
        self.energy_consumption = self.energy_data[0]
        self.peak_load = self.energy_data[1]
        self.system_covered = None
        self.system = {0: 'Off Grid System', 1: 'Stable Grid connection', 2: 'Unstable Grid connection'}
        self.power_sink = pd.DataFrame(columns=['Time', 'P [W]'])
        self.power_sink = self.power_sink.set_index('Time')
        self.power_sink_max = None
        self.df = self.build_df()
        self.dispatch()
        # self.energy_supply_parameters = self.calc_energy_parameters()
        # self.evaluation_df = self.evaluate_system()
        self.export_data()

    ''' Basic Functions'''
    def build_df(self):
        """
        Assign columns to pd.DataFrame
        :return: pd.DataFrame
            DataFrame with component columns
        """
        df = pd.DataFrame(columns=['Load [W]', 'P_Res [W]'],
                          index=self.env.time)
        df['Load [W]'] = self.env.df['P_Res [W]']
        df['P_Res [W]'] = self.env.df['P_Res [W]']
        if self.env.grid_connection:
            if self.env.blackout:
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

    ''' Simulation '''
    def dispatch(self):
        """
        dispatch:
        Basic priorities
            1) RE self-consumption
            2) Charge storage from RE
        :return: None
        """
        env = self.env
        # Time step iteration
        for clock in self.df.index:
            for component in env.re_supply:
                # Priority 1: RE self supply
                self.re_self_supply(clock=clock,
                                    component=component)
                # Priority 2: Charge Storage from RE
                for es in env.storage:
                    self.re_charge(clock=clock,
                                   es=es,
                                   component=component)
            if env.grid_connection is True:
                # system with grid connection
                if env.blackout is False:
                    # stable grid connection
                    self.stable_grid(clock=clock)
                else:
                    # Unstable grid connection
                    self.unstable_grid(clock=clock)
            else:
                # Off grid system
                self.off_grid(clock=clock)
        for pv in self.env.pv:
            col = pv.name + ' [W]'
            self.df[col] = np.where(self.df[col] < 0, 0, self.df[col])
        if self.env.feed_in is True:
            for component in env.re_supply:
                self.feed_in(component=component)
        power_sink = self.check_dispatch()
        self.power_sink = pd.concat([self.power_sink, power_sink])
        if len(self.power_sink) == 0:
            self.power_sink_max = 0
            self.system_covered = True
        else:
            self.power_sink_max = float(self.power_sink.max().iloc[0])
            self.system_covered = False

    def check_dispatch(self):
        """
        Check if all load is covered with current system components
        :return: None
        """
        power_sink = {}
        for clock in self.df.index:
            if self.df.loc[clock, 'P_Res [W]'] > 0:
                power_sink[clock] = self.df.loc[clock, 'P_Res [W]']
        power_sink_df = pd.DataFrame(power_sink.items(),
                                     columns=['Time', 'P [W]'])
        power_sink_df = power_sink_df.set_index('Time')
        power_sink_df = power_sink_df.round(2)

        return power_sink_df

    def stable_grid(self, clock: dt.datetime):
        """
        Dispatch strategy from stable grid connection
            Stable grid connection:
                3) Cover residual load from Storage
                4) Cover residual load from Grid
        :param clock: dt.datetime
            time stamp
        :return: None
        """
        env = self.env
        for es in env.storage:
            if self.df.loc[clock, 'P_Res [W]'] > 0:
                power = self.df.loc[clock, 'P_Res [W]']
                discharge_power = es.discharge(clock=clock,
                                               power=power)
                self.df.loc[clock, es.name + ' [W]'] += discharge_power
                self.df.loc[clock, 'P_Res [W]'] += discharge_power
        # Priority 4: Cover load from grid
        self.grid_profile(clock=clock)

    def unstable_grid(self, clock: dt.datetime):
        """
        Dispatch strategy for unstable grid connection
            No Blackout:
                3) Cover residual load from Grid
            Blackout:
                4.1) Cover load from Storage
                4.2) Cover load from Diesel Generator
        :param clock: dt.datetime
            time stamp
        :return: None
        """
        env = self.env
        if not env.df.loc[clock, 'Blackout']:
            self.grid_profile(clock=clock)
        else:
            for es in env.storage:
                if self.df.loc[clock, 'P_Res [W]'] > 0:
                    power = self.df.loc[clock, 'P_Res [W]']
                    discharge_power = es.discharge(clock=clock,
                                                   power=power)
                    self.df.loc[clock, es.name + ' [W]'] += discharge_power
                    self.df.loc[clock, 'P_Res [W]'] += discharge_power
            for dg in env.diesel_generator:
                self.dg_profile(clock=clock,
                                dg=dg)

    def off_grid(self, clock: dt.datetime):
        """
        Dispatch strategy for Off-grid systems
            1) RE self consumption
            2) Charge storage from RE
            Diesel Generator with low load behavior:
                3) Cover load from Storage
                4) Cover load from Diesel Generator
            Diesel Generator with no low load behavior:
        :param clock: dt.datetime
            time stamp
        :return: None
        """
        env = self.env
        for es in env.storage:
            if self.df.loc[clock, 'P_Res [W]'] > 0:
                power = self.df.loc[clock, 'P_Res [W]']
                discharge_power = es.discharge(clock=clock,
                                               power=power)
                self.df.loc[clock, es.name + ' [W]'] += discharge_power
                self.df.loc[clock, 'P_Res [W]'] += discharge_power
        for dg in env.diesel_generator:
            self.dg_profile(clock=clock,
                            dg=dg)

    def feed_in(self, component: PV or WindTurbine):
        """
        Calculate RE feed-in power and revenues
        :param component: PV/WindTurbine
        :return: None
        """
        if self.env.grid_connection is False:
            pass
        else:
            self.df[component.name + ' Feed in [W]'] = self.df[component.name + ' remain [W]']
            if isinstance(component, PV):
                self.df[component.name + f' Feed in [{self.env.currency}]'] \
                    = self.df[component.name + ' Feed in [W]'] * self.env.i_step / 60 / 1000 * self.env.pv_feed_in_tariff
            elif isinstance(component, WindTurbine):
                self.df[component.name + f' Feed in [{self.env.currency}]'] \
                    = self.df[component.name + ' Feed in [W]'] * self.env.i_step / 60 / 1000 * self.env.wt_feed_in_tariff

    def re_self_supply(self, clock: dt.datetime, component: PV or WindTurbine):
        """
        Calculate re self-consumption
        :param clock: dt.datetime
             time stamp
        :param component: PV/Windturbine
            RE component
        :return: None
        """
        df = self.df
        df.loc[clock, component.name + ' [W]'] = np.where(
            df.loc[clock, 'P_Res [W]'] > component.df.loc[clock, 'P [W]'],
            component.df.loc[clock, 'P [W]'], df.loc[clock, 'P_Res [W]'])
        df.loc[clock, component.name + ' [W]'] = np.where(
            df.loc[clock, component.name + ' [W]'] < 0, 0, df.loc[clock, component.name + ' [W]'])
        df.loc[clock, component.name + ' remain [W]'] = np.where(
            component.df.loc[clock, 'P [W]'] - df.loc[clock, 'P_Res [W]'] < 0,
            0, component.df.loc[clock, 'P [W]'] - df.loc[clock, 'P_Res [W]'])
        df.loc[clock, 'P_Res [W]'] -= df.loc[clock, component.name + ' [W]']
        if df.loc[clock, 'P_Res [W]'] < 0:
            df.loc[clock, 'P_Res [W]'] = 0

    def re_charge(self, clock: dt.datetime, es: Storage, component: PV or WindTurbine):
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
        self.df.loc[clock, es.name + ' [W]'] = charge_power
        self.df.loc[clock, component.name + '_charge [W]'] = charge_power
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

    def dg_profile(self, clock: dt.datetime, dg: DieselGenerator):
        """
        Cover load from Diesel Generator

        :param clock: dt.datetime
            tome stamp
        :param dg: object
            Diesel Generator
        :return: None
        """
        power = self.df.loc[clock, 'P_Res [W]']
        self.df.loc[clock, dg.name + ' [W]'] = dg.run(clock=clock,
                                                      power=power)
        self.df.loc[clock, 'P_Res [W]'] -= self.df.loc[clock, dg.name + ' [W]']

    def export_data(self):
        """
        Export data after simulation
        :return: None
        """
        sep = self.env.csv_sep
        decimal = self.env.csv_decimal
        root = sys.path[1]
        self.df.to_csv(root + '/export/operator.csv', sep=sep, decimal=decimal)
        self.env.weather_data[0].to_csv(root + '/export/weather_data.csv', sep=sep, decimal=decimal)
        self.env.wt_weather_data.to_csv(root + '/export/wt_weather_data.csv', sep=sep, decimal=decimal)
        self.env.monthly_weather_data.to_csv(root + '/export/monthly_weather_data.csv', sep=sep, decimal=decimal)
