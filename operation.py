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
        self.evaluation = self.evaluate_system()
        print(self.evaluation)

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
        dispatch dispatch:
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
        power_sink = self.check_dispatch()
        self.power_sink = pd.concat([self.power_sink, power_sink])
        self.power_sink_max = float(self.power_sink.max())
        if len(self.power_sink) > 0:
            self.system_covered = False
            # print('Residual load is not covered with current system components. ' + str(self.power_sink_max) + ' W missing.')
        else:
            self.system_covered = True

    def check_dispatch(self):
        """
        Check if all load is covered with current system components
        :return:
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
        if env.df.loc[clock, 'Blackout'] is False:
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

    def re_self_supply(self, clock: dt.datetime, component: object):
        """
        Calculate re self-consumption
        :param clock: dt.datetime
             time stamp
        :param component: object
            re component (pv, wind turbine)
        :return: None
        """
        if isinstance(component, PV) or isinstance(component, WindTurbine):
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
        :return:
        """
        pv_energy = 0
        wt_energy = 0
        grid_energy = 0
        dg_energy = 0
        es_charge = 0
        es_discharge = 0
        charge_values = []
        discharge_values = []
        for pv in self.env.pv:
            col = pv.name + ' [W]'
            pv_energy += self.df[col].sum() * self.env.i_step / 60 / 1000
        for wt in self.env.wind_turbine:
            col = wt.name + ' [W]'
            wt_energy += self.df[col].sum() * self.env.i_step / 60 / 1000
        for grid in self.env.grid:
            col = grid.name + ' [W]'
            grid_energy += self.df[col].sum() * self.env.i_step / 60 / 1000
        for dg in self.env.diesel_generator:
            col = dg.name + ' [W]'
            dg_energy += self.df[col].sum() * self.env.i_step / 60 / 1000
        for es in self.env.storage:
            col = es.name + ' [W]'
            charge_values.extend(np.where(self.df[col] > 0, self.df[col], 0).tolist())
            discharge_values.extend(np.where(self.df[col] < 0, self.df[col], 0).tolist())
            es_charge += sum(charge_values) * self.env.i_step / 60 / 1000
            es_discharge += sum(discharge_values) * self.env.i_step / 60 / 1000

        return pv_energy, wt_energy, grid_energy, dg_energy, es_charge, es_discharge

    ''' Economical and Ecological parameters '''

    def evaluate_system(self):
        """

        :return:
        """
        env = self.env
        pv_lcoe = {}
        wt_lcoe = {}
        dg_lcoe = {}
        for pv in env.pv:
            lcoe = self.economic_evaluation(pv)
            pv_lcoe[pv.name] = lcoe
        for wt in env.wind_turbine:
            lcoe = self.economic_evaluation(wt)
            wt_lcoe[wt.name] = lcoe
        for dg in env.diesel_generator:
            lcoe = self.economic_evaluation(dg)
            dg_lcoe[dg.name] = lcoe

        return pv_lcoe, wt_lcoe, dg_lcoe

    def economic_evaluation(self, component: DieselGenerator or PV or WindTurbine):
        """
        Calculate component levelized cot of energy (LCOE)
        :param component: object
            energy supply component
        :return: float
            LCOE
        """
        capital_cost = component.c_invest_n * component.p_n / 1000
        # Get component specific parameters
        if isinstance(component, PV):
            annual_operating_cost = component.c_op_main_n * component.p_n / 1000
            annual_output = self.energy_supply_parameters[0]
        elif isinstance(component, WindTurbine):
            annual_operating_cost = component.c_op_main_n * component.p_n / 1000
            annual_output = self.energy_supply_parameters[1]
        else:
            annual_output = self.energy_supply_parameters[3]
            fuel_cost = component.df['Fuel cost [' + self.env.currency + ']'].sum()
            annual_operating_cost = component.c_op_main_n * component.p_n / 1000 + annual_output * component.c_var + fuel_cost
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
        l = self.env.lifetime
        d = self.env.d_rate
        lcoe = py_lcoe(annual_output=annual_output,
                       annual_operating_cost=annual_operating_cost,
                       capital_cost=capital_cost,
                       discount_rate=d,
                       lifetime=l)
        return lcoe


if __name__ == '__main__':
    start_time = time.time()
    start = dt.datetime(year=2021, month=1, day=1, hour=0, minute=0)
    end = dt.datetime(year=2021, month=1, day=1, hour=23, minute=59)
    environment = Environment(name='St. Dominics Hospital',
                              time={'start': start, 'end': end, 'step': dt.timedelta(minutes=15), 'timezone': 'CET'},
                              location={'longitude': -0.7983,
                                        'latitude': 6.0442,
                                        'altitude': 50,
                                        'roughness_length': 'Open terrain with smooth surface, e.g., concrete, airport runways, mowed grass'},
                              grid_connection=False, blackout=False)
    load_profile = 'C:/Users/Rummeny/PycharmProjects/MiGUEL_Fulltime/data/load/St. Dominics Hospital.csv'
    environment.add_load(load_profile=load_profile)
    # environment.add_pv(p_n=65000,
    #                    pv_data={'surface_tilt': 20, 'surface_azimuth': 180, 'min_module_power': 250,
    #                             'max_module_power': 350, 'inverter_power_range': 25000})
    # environment.add_grid()
    environment.add_wind_turbine(p_n=4200000, turbine_data={"turbine_type": "E-126/4200", "hub_height": 135})
    environment.add_diesel_generator(p_n=30000, fuel_consumption=9.7, fuel_price=1.20)
    environment.add_storage(p_n=10000, c=50000, soc=0.5)
    operator = Operator(env=environment)
    # report = Report(environment=environment, operator=operator)
    # print(operator.df)
    # operator.df.plot()
    # plt.show()
    print('Runtime: %s seconds' % (time.time() - start_time))
