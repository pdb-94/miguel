import sys
import time
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
# MiGUEL modules
from report.report import Report
from environment import Environment
from pv import PV
from dieselgenerator import DieselGenerator
from windturbine import WindTurbine
from storage import Storage
from grid import Grid
from lcoe.lcoe import lcoe as py_lcoe


class Operator:
    """
    Class to control environment, dispatch dispatch and parameter optimization
    """

    def __init__(self,
                 env: Environment):
        """
        :param env: Environment
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
        self.energy_supply_parameters = self.calc_energy_parameters()
        self.evaluation_df = self.evaluate_system()
        self.export_data()

    ''' Basic Functions'''
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
                self.re_self_supply(clock=clock, component=component)
                # Priority 2: Charge Storage from RE
                for es in env.storage:
                    self.re_charge(clock=clock, es=es, component=component)
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
            self.system_covered = False
        else:
            self.power_sink_max = float(self.power_sink.max().iloc[0])
            self.system_covered = True

    def check_dispatch(self):
        """
        Check if all load is covered with current system components
        :return: None
        """
        power_sink = {}
        for clock in self.df.index:
            if self.df.loc[clock, 'P_Res [W]'] > 0:
                power_sink[clock] = self.df.loc[clock, 'P_Res [W]']
        power_sink_df = pd.DataFrame(power_sink.items(), columns=['Time', 'P [W]'])
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
                discharge_power = es.discharge(clock=clock, power=power)
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
                    discharge_power = es.discharge(clock=clock, power=power)
                    self.df.loc[clock, es.name + ' [W]'] += discharge_power
                    self.df.loc[clock, 'P_Res [W]'] += discharge_power
            for dg in env.diesel_generator:
                self.dg_profile(clock=clock, dg=dg)

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
                discharge_power = es.discharge(clock=clock, power=power)
                self.df.loc[clock, es.name + ' [W]'] += discharge_power
                self.df.loc[clock, 'P_Res [W]'] += discharge_power
        for dg in env.diesel_generator:
            self.dg_profile(clock=clock, dg=dg)

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
                self.df[component.name + ' Feed in [' + self.env.currency + ']'] \
                    = self.df[component.name + ' Feed in [W]'] * self.env.i_step / 60 / 1000 * self.env.pv_feed_in_tariff
            elif isinstance(component, WindTurbine):
                self.df[component.name + ' Feed in [' + self.env.currency + ']'] \
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
        self.df.loc[clock, dg.name + ' [W]'] = dg.run(clock=clock, power=power)
        self.df.loc[clock, 'P_Res [W]'] -= self.df.loc[clock, dg.name + ' [W]']

    def calc_energy_parameters(self):
        """
        Calculate total energy supply for each component group.
        :return:float
            annual energy supply [kWh/a]
        """
        pv_energy = {}
        wt_energy = {}
        grid_energy = {}
        dg_energy = {}
        es_charge = {}
        es_discharge = {}
        for pv in self.env.pv:
            col = pv.name + ' [W]'
            pv_energy[pv.name] = self.df[col].sum() * self.env.i_step / 60 / 1000
        for wt in self.env.wind_turbine:
            col = wt.name + ' [W]'
            wt_energy[wt.name] = self.df[col].sum() * self.env.i_step / 60 / 1000
        for grid in self.env.grid:
            col = grid.name + ' [W]'
            grid_energy[grid.name] = self.df[col].sum() * self.env.i_step / 60 / 1000
        for dg in self.env.diesel_generator:
            col = dg.name + ' [W]'
            dg_energy[dg.name] = self.df[col].sum() * self.env.i_step / 60 / 1000
        for es in self.env.storage:
            col = es.name + ' [W]'
            charge_values = []
            discharge_values = []
            charge_values.extend(np.where(self.df[col] > 0, self.df[col], 0).tolist())
            discharge_values.extend(np.where(self.df[col] < 0, self.df[col], 0).tolist())
            es_charge[es.name] = sum(charge_values) * self.env.i_step / 60 / 1000
            es_discharge[es.name] = sum(discharge_values) * self.env.i_step / 60 / 1000

        return pv_energy, wt_energy, grid_energy, dg_energy, es_charge, es_discharge

    ''' Economical and Ecological parameters '''
    def evaluate_system(self):
        """
        Evaluate the system configuration
        :return: Dict
            LCOE and CO2-emissions
        """
        df = pd.DataFrame(columns=['Component',
                                   'Energy production [kWh]',
                                   'LCOE [' + self.env.currency + '/kWh]',
                                   'Total CO2-emissions [t]',
                                   'Initial CO2-emissions [t]',
                                   'Annual CO2-emissions [t/a]'])
        env = self.env
        lifetime = self.env.lifetime
        for pv in env.pv:
            co2 = self.ecological_evaluation(pv)
            lcoe = self.economic_evaluation(component=pv, co2=co2[0]/lifetime)
            parameters = [pv.name, self.energy_supply_parameters[0][pv.name]*lifetime, lcoe, co2[0], co2[1], co2[2]]
            df.loc[len(df)] = parameters
        for wt in env.wind_turbine:
            co2 = self.ecological_evaluation(wt)
            lcoe = self.economic_evaluation(component=wt, co2=co2[0]/lifetime)
            parameters = [wt.name, self.energy_supply_parameters[1][wt.name]*lifetime, lcoe, co2[0], co2[1], co2[2]]
            df.loc[len(df)] = parameters
        for grid in env.grid:
            co2 = self.ecological_evaluation(grid)
            lcoe = self.economic_evaluation(component=grid, co2=co2[0]/lifetime)
            parameters = [grid.name, self.energy_supply_parameters[2][grid.name]*lifetime, lcoe, co2[0], co2[1], co2[2]]
            df.loc[len(df)] = parameters
        for dg in env.diesel_generator:
            co2 = self.ecological_evaluation(dg)
            lcoe = self.economic_evaluation(component=dg, co2=co2[0]/lifetime)
            parameters = [dg.name, self.energy_supply_parameters[3][dg.name]*lifetime, lcoe, co2[0], co2[1], co2[2]]
            df.loc[len(df)] = parameters
        for es in env.storage:
            co2 = self.ecological_evaluation(es)
            lcoe = self.economic_evaluation(component=es, co2=co2[0]/lifetime)
            parameters = [es.name, self.energy_supply_parameters[4][es.name]*lifetime, lcoe, co2[0], co2[1], co2[2]]
            df.loc[len(df)] = parameters

        # Calculate System LCOE and CO2-Emissions
        system_co2 = self.total_co2_emissions(df=df)
        system_lcoe = self.total_lcoe(df=df)
        system_parameters = ['System', self.energy_consumption*self.env.lifetime, system_lcoe, system_co2[0], system_co2[1], system_co2[2]]
        df.loc[len(df)] = system_parameters

        return df

    def economic_evaluation(self, component: object, co2: float):
        """
        Calculate component levelized cot of energy (LCOE)
        :param component: object
            energy supply component
        :param co2: float
            annual co2_emissions
        :return: float
            LCOE
        """
        env = self.env
        name = component.name
        # Get component specific parameters
        if isinstance(component, PV):
            capital_cost = component.c_invest_n * component.p_n / 1000
            if env.feed_in is False or env.grid_connection is False:
                annual_revenues = 0
            else:
                annual_revenues = self.df[component.name + ' Feed in [' + env.currency + ']'].sum()
            annual_cost = component.c_op_main_n * component.p_n / 1000
            co2_cost = co2 * env.avg_co2_price
            annual_operating_cost = annual_cost - annual_revenues + co2_cost
            annual_output = self.energy_supply_parameters[0][name]
        elif isinstance(component, WindTurbine):
            capital_cost = component.c_invest_n * component.p_n / 1000
            if env.feed_in is False or env.grid_connection is False:
                annual_revenues = 0
            else:
                annual_revenues = self.df[component.name + ' Feed in [' + env.currency + ']'].sum()
            annual_cost = component.c_op_main_n * component.p_n / 1000
            co2_cost = co2 * env.avg_co2_price
            annual_operating_cost = annual_cost - annual_revenues + co2_cost
            annual_output = self.energy_supply_parameters[1][name]
        elif isinstance(component, Grid):
            capital_cost = 0
            annual_output = self.energy_supply_parameters[2][name]
            co2_cost = co2 * env.avg_co2_price
            annual_operating_cost = annual_output * env.electricity_price + co2_cost
        elif isinstance(component, DieselGenerator):
            capital_cost = component.c_invest_n * component.p_n / 1000
            annual_output = self.energy_supply_parameters[3][name]
            co2_cost = co2 * env.avg_co2_price
            fuel_cost = component.df['Fuel cost [' + env.currency + ']'].sum()
            annual_operating_cost = component.c_op_main_n * component.p_n / 1000 + annual_output * component.c_var + fuel_cost + co2_cost
        elif isinstance(component, Storage):
            capital_cost = component.c_invest_n * component.c / 1000 + component.total_replacement_cost
            co2_cost = co2 * env.avg_co2_price
            annual_output = abs(self.energy_supply_parameters[5][name])
            annual_operating_cost = component.c_op_main_n * component.c / 1000 + co2_cost
        else:
            return None
        if annual_output == 0:
            return None
        # Calculate LCOE
        lcoe = self.calc_lcoe(capital_cost=capital_cost,
                              annual_operating_cost=annual_operating_cost,
                              annual_output=annual_output)
        return lcoe

    def calc_lcoe(self, capital_cost, annual_operating_cost, annual_output):
        """
        Calculate LCOE with given parameters
        :param capital_cost: float
        :param annual_operating_cost: float
        :param annual_output: float
        :return: float
            LCOE
        """
        lcoe = py_lcoe(annual_output=annual_output,
                       annual_operating_cost=annual_operating_cost,
                       capital_cost=capital_cost,
                       discount_rate=self.env.d_rate,
                       lifetime=self.env.lifetime)
        return lcoe

    def ecological_evaluation(self, component: object):
        """
        Calculate CO2-emissions
        :param component: object
            energy supply component
        :return: float
            CO2-emissions
        """
        name = component.name
        if isinstance(component, PV):
            annual_output = self.energy_supply_parameters[0][name]
            co2_o = 0
            co2_init = component.co2_init * component.p_n / 1e6
        elif isinstance(component, WindTurbine):
            annual_output = self.energy_supply_parameters[1][name]
            co2_o = 0
            co2_init = component.co2_init * component.p_n / 1e6
        elif isinstance(component, Grid):
            annual_output = self.energy_supply_parameters[2][name]
            co2_o = self.env.co2_grid
            co2_init = 0
        elif isinstance(component, DieselGenerator):
            annual_output = self.energy_supply_parameters[3][name]
            co2_o = self.env.co2_diesel
            co2_init = component.co2_init * component.p_n / 1e6
        elif isinstance(component, Storage):
            annual_output = self.energy_supply_parameters[5][name]
            co2_o = 0
            co2_init = component.co2_init * component.c / 1e6 * component.replacements
        else:
            return None
        # Calculate annual and total CO2-emissions
        co2_annual = co2_o * annual_output / 1000
        co2_emissions = co2_init + co2_annual * self.env.lifetime

        return co2_emissions, co2_init, co2_annual

    def total_lcoe(self, df: pd.DataFrame):
        """
        Calculate system LCOE
        :param df: pd.DataFrame
            Component evaluation parameters
        :return: float
            system lcoe
        """
        system_lcoe = 0
        for i in range(len(df)):
            if df.loc[i, 'LCOE [' + self.env.currency + '/kWh]'] is not None:
                system_lcoe += df.loc[i, 'LCOE [' + self.env.currency + '/kWh]'] \
                               * df.loc[i, 'Energy production [kWh]'] / (self.energy_consumption*self.env.lifetime)
        system_lcoe = system_lcoe

        return system_lcoe

    def total_co2_emissions(self, df: pd.DataFrame):
        """
        Calculate system CO2-emissions
        :param df: pd.DataFrame
            Component evaluation parameters
        :return: float
            system CO2-emissions
        """
        total_co2_emission = df['Total CO2-emissions [t]'].sum()
        initial_co2_emission = df['Initial CO2-emissions [t]'].sum()
        annual_co2_emission = df['Annual CO2-emissions [t/a]'].sum()

        return total_co2_emission, initial_co2_emission, annual_co2_emission

    def export_data(self):
        """
        Export data after simulation
        :return: None
        """
        root = sys.path[1]
        self.df.to_csv(root + '/export/operator.csv', sep=',', decimal='.')
        self.env.weather_data[0].to_csv(root + '/export/weather_data.csv', sep=',', decimal='.')
        self.env.wt_weather_data.to_csv(root + '/export/wt_weather_data.csv', sep=',', decimal='.')
        self.env.monthly_weather_data.to_csv(root + '/export/monthly_weather_data.csv', sep=',', decimal='.')
