import pandas as pd
import numpy as np
import datetime as dt
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt


class Electrolyser:
    def __init__(self,
                 env= None,
                 name: str= None,
                 p_n: float = None,
                 c_invest_n: float=1854.6,  # Euro/kw
                 c_invest: float= None,
                 c_op_main_n: float=18.55,  #Euro/kw
                 c_op_main: float = None,
                 co2_init: float = 36.95, # kg co2/kW für einen PEM Electrolyser
                 c_var_n: float = 0,
                 life_time: float = None):

        self.env = env
        self.p_n = p_n
        self.name = name
        self.p_min = 10
        self.efficiency_electrolyser = None

        self.df_electrolyser = pd.DataFrame(columns=['P[W]',
                                        'P[%]',
                                        'H2_Production [kg]',
                                        'LCOH [$/kg]'], index=self. env.time)
        # Economic parameters
        self.c_invest_n = c_invest_n    #USD/kw
        self.c_var_n = c_var_n          #USD/kW
        if c_invest is None:
           self.c_invest = c_invest_n * self.p_n / 1000
        else:
            self.c_invest = c_invest
        if c_op_main_n is not None:
            self.c_op_main_n = c_op_main_n
        else:
            self.c_op_main_n = self.c_invest_n * 0.03  # USD/kW
        #Operation Cost
        self.c_op_main_n= c_op_main_n
        if c_op_main is None:
            self. c_op_main = self.c_op_main_n * self.p_n / 1000
        else:
            self.c_op_main = c_op_main
        #Co2 Cost
        self.co2_init = co2_init * self.p_n/1000   # kg

        self.life_time=life_time

        # Technical data
        self.technical_data = { 'component': 'Elektrolyseur',
                               'Name': self.name,
                               'Nominal power [kW]': round ( self.p_n/1000, 3),
                               f'specific investment cost [US$/kW]': int(self.c_invest_n),
                               f'investment cost [US$]': int(self.c_invest),
                               f'specific operation maintenance cost[US $/ kW]': int(self.c_op_main_n),
                               f'operation maintenance cost [US$/a]': int(self.c_op_main_n * self.p_n / 1000)}

    def run (self,
             clock,
             power: float):
        """
        Run Electrolyser
        :param clock: dt.datetime
               time stamp
        :param power: float
               power[W]
        :return: clock power
        """
        power = min(power, self.p_n)
        p_relative = round(((power/self.p_n) * 100),2)
        self.df_electrolyser.at[clock, 'P[%]'] = p_relative

        efficiency = self.calc_efficiency(p_rel=p_relative)
        print(f"EFFICIENCY ELEKTROLYSEUR :{efficiency}")
        self.df_electrolyser.at[clock, 'Efficiency'] = round(efficiency, 2)

        if p_relative >= self.p_min:      # Bedingung minimale Leisteung
            h2_production = self. calc_H2_production(clock, power=power, eff=efficiency)
            #set values
            self.df_electrolyser.at[clock, 'P[W]'] = round(power,2)
            self.df_electrolyser.at[clock, 'P[%]'] = p_relative
            self.df_electrolyser.at[clock, 'H2_Production [kg]'] = h2_production

        else:
            self.df_electrolyser.at[clock, 'P[W]'] = 0
            self.df_electrolyser.at[clock, 'P[%]'] = 0
            self.df_electrolyser.at[clock, 'H2_Production [kg]'] = 0


    def calc_efficiency(self,p_rel: float = None) -> float:
        """
        Parametrised parabolic efficiency curve:
        η = (-Δη / 0.49) * ((P_el / P_cap - P_eta_max)^2) + η_max

        :param power: current power in W
        :param eta_max: maximum efficiency
        :param eta_min: minimum efficiency
        :param p_rel: optional relative power in percent (0–100); if None, computed from power
        :return: efficiency (clipped to 0–1)
        """
        p_eta_max = 0.3  # Relative point (0–1) at which maximum efficiency occurs
        eta_max= 0.75
        eta_min = 0.60

        if p_rel==0:
            efficiency=0
        else:
            p_rel = p_rel / 100  # convert from percent to [0–1]

        delta_eta = eta_max - eta_min
        efficiency = (-delta_eta / 0.49) * ((p_rel - p_eta_max) ** 2) + eta_max

        return efficiency

    def calc_H2_production(self, clock: dt.datetime, power: float, eff: float):
        """
        Berechnung der H2-Produktion nach Wirkungsgradformel:
        ṁ = (η * P_el) / LHV_H2
        :param power: elektrische Leistung [W]
        :param eff: Effizienz (0-1)
        :return: H2-Produktion in kg
        """
        energy = round((power) * (self.env.i_step / 60), 2)  # [Wh], bei i_step in Minuten
        h2_production = round((energy * eff) / (33.33 * 1000), 2)  # 33.33 kWh/kg, Umrechnung Wh → kWh

        self.df_electrolyser.at[clock, 'H2_Production [kg]'] = max(0, h2_production)

        return h2_production


    '''
   def calc_efficiency(self, p_rel: float):
        """
        Calculates the efficiency of the electrolyser based on the current power.
        Efficiency equation:
        η = -0.1096 * (P/P_nom)^2 + 0.0060 * (P/P_nom) + 0.8952
        :param power: current power in W
        :return: efficiency (0-1)
        """
        if self.p_n == 0:
            return 0  # Avoid division by zero
        p_rel = p_rel / 100  # Umrechnung von Prozent in [0–1]
        efficiency = -0.1096 * (p_rel ** 2) + 0.0060 * p_rel + 0.8952
        return max(0, efficiency)
    '''















































