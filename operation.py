import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
# MiGUEL modules
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
                 env: en.Environment,
                 dispatch_strategy: str = None):
        """
        :param env:
        :param dispatch_strategy: str
        """
        self.env = env
        self.dispatch_strategy = dispatch_strategy
        # self.run(dispatch_strategy=self.dispatch_strategy)

    def run(self, dispatch_strategy: str = None):
        """
        run dispatch
        :param dispatch_strategy: str
            dispatch strategy to execute
        :return: None
        """
        if dispatch_strategy == 'dispatch_1':
            self.dispatch_1()
        elif dispatch_strategy == 'dispatch_2':
            self.dispatch_2()
        elif dispatch_strategy == 'dispatch_3':
            self.dispatch_3()

    def dispatch_1(self):
        """
        dispatch strategy 1:
            Components: PV-System, Wind Turbine, Load, Grid
            - reliable grid connection (no blackouts)
            - max. RE self-consumption
            - Feed-in possible
            - Remaining load covered by grid
        :return: None
        """
        env = self.env
        env.df['PV feed in [W]'] = 0
        env.df['WT feed in [W]'] = 0
        env.calc_self_supply()
        for grid in env.grid:
            env.df[grid.name + ': P [W]'] = env.df['P_Res (after RE) [W]']
        # Calculate PV WT Feed in Power
        # for pv in env.pv:
        #     env.df['PV feed in [W]'] -=
        # for wt in env.wind_turbine:
        #     env.df['WT feed in [W]'] -=

    def dispatch_2(self):
        """
        dispatch strategy 2:
            Components: PV-System, Wind Turbine, Load, Diesel Generator, Grid, Storage
            - Grid connection with Blackouts
            - Max. RE self-consumption
            - Remaining RE to charge Storage
            - Cover remaining load through Diesel Generator, Storage, Grid
            - Cover remaining load through Blackout with Diesel Generator, Storage
        :return: None
        """
        env = self.env
        env.calc_self_supply()

    def dispatch_3(self):
        """
        dispatch strategy 3:
            Components: PV-System, Wind Turbine, Load, Diesel Generator
            - Off grid system
            - max. PV/WT self-consumption
            - Curtail remaining PV/WT production
            - Cover remaining load with Diesel Generator
        :return: None
        """
        env = self.env
        # Calculate PV Curtailment
        env.df['PV Curtail [W]'] = 0
        pv_curtail = env.df['P_Res [W]'] - env.df['PV total power [W]']
        env.df['PV Curtail [W]'] = np.where(pv_curtail > 0, 0, pv_curtail)
        # Calculate WT Curtailment
        env.df['WT Curtail [W]'] = 0
        wt_curtail = env.df['P_Res [W]'] - env.df['WT total power [W]']
        env.df['WT Curtail [W]'] = np.where(wt_curtail > 0, 0, wt_curtail)
        env.calc_self_supply()
        # Run generator model
        for generator in env.diesel_generator:
            generator.run()
            env.df[generator.name + ': P [W]'] = generator.df['P [W]'].values
        # Calculate RE load
        re_load_adjusted = env.df['P_Res [W]'] - env.df['Diesel Generator_1: P [W]']
        env.df['RE self consumption [W]'] = np.where(re_load_adjusted > env.df['Self supply [W]'],
                                                     env.df['Self supply [W]'],
                                                     re_load_adjusted)
        env.df['RE Curtailment adjusted [W]'] = -(env.df['Self supply [W]'] - env.df['RE self consumption [W]'])

    def system_comparison(self, component: str = None):
        """
        TODO: Compare system components, single components and all components. Optimization based on levelized cost of energy
            - PV/WT plant size
            - Diesel generator model
            - ES Y/N (size)
            - Problem:
                - all components influence each other (recursive behavior)
                - Optimize runtime
                    - Extract weather data while initiating Environment
                      (Env will only be created once - Components more often)
                    -

        :param component: str
            system component to compare
        :return: None
        """

        if component == 'Diesel Generator':
            print('Compare Diesel Generator with Generator Model.')
        elif component == 'PV':
            print('Compare PV plant size.')
        elif component == 'WT':
            print('Compare System')


if __name__ == '__main__':
    start = dt.datetime(year=2021, month=1, day=1, hour=0, minute=0)
    end = dt.datetime(year=2021, month=1, day=31, hour=23, minute=59)
    environment = en.Environment(time={'start': start, 'end': end, 'step': dt.timedelta(minutes=1), 'timezone': 'CET'},
                                 location={'longitude': -0.7983,
                                           'latitude': 6.0442,
                                           'altitude': 50,
                                           'roughness_length': 'Open terrain with smooth surface, e.g., concrete, airport runways, mowed grass'})
    load_profile = 'C:/Users/Rummeny/PycharmProjects/MiGUEL_Fulltime/data/load/St. Dominics Hospital.csv'
    environment.add_load(load_profile=load_profile)
    print('Load created')
    environment.add_pv(p_n=None,
                       pv_profile=None,
                       pv_module='ET_Solar_Industry_ET_A_M672285B',
                       inverter='ABB__PVI_3_0_OUTD_S_US__208V_',
                       modules_per_string=4,
                       strings_per_inverter=2,
                       surface_tilt=20,
                       surface_azimuth=180)
    environment.add_pv(p_n=None,
                       pv_profile=None,
                       pv_module='ET_Solar_Industry_ET_A_M672285B',
                       inverter='ABB__PVI_3_0_OUTD_S_US__208V_',
                       modules_per_string=6,
                       strings_per_inverter=3,
                       surface_tilt=20,
                       surface_azimuth=180)
    print('PV created')
    environment.add_grid()
    print('Grid created')
    environment.add_wind_turbine(p_n=4200, turbine_data={"turbine_type": "E-126/4200", "hub_height": 135})
    print('WT created')
    environment.add_diesel_generator(p_n=10000, fuel_consumption=9.7, fuel_price=1.20, low_load_behavior=False)
    print('DG created')
    environment.add_storage(p_n=50, c=50)
    print('ES created')
    environment.calc_self_supply()
    operator = Operator(env=environment, dispatch_strategy='dispatch_1')
    report = Report(environment=environment, operator=operator)
    # operator.env.df.to_csv('env.csv')
    # operator.env.df[['P_Res [W]', 'Self supply [W]', 'Diesel Generator_1: P [W]', 'RE self consumption [W]']].plot()
    # operator.env.df[['P_Res [W]', 'Self supply [W]', 'Wind Turbine_1: P [W]', 'Grid_1: P [W]']].plot()
    # plt.show()
