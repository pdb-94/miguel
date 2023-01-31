import numpy_financial as npf
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
from pv import PV
from dieselgenerator import DieselGenerator
from windturbine import WindTurbine
from storage import Storage


class Evaluation:
    """
    Class for the evaluation of the system from an economic and ecological point of view
    """

    def __init__(self,
                 operator=None,
                 environment=None):
        self.operator = operator
        self.env = environment

    def calc_lcoe(self, component: DieselGenerator or PV or WindTurbine):
        """

        :param component: object
            system component
        :return:
        """
        name = component.name
        p_n = component.name
        c_invest = component.c_invest * p_n / 1000
        c_o_m = component.c_op_maon * p_n / 1000
        energy = self.operator.df[name + ' [W]'].sum() * self.env.i_step / 60 / 1000
        l = self.env.lifetime
        i = self.env.i_rate
        lcoe = 0
        if isinstance(component, DieselGenerator):
            fuel_cost = component.df['Fuel cost [' + self.env.currency + ']'].sum()
            annual_cost = c_o_m + fuel_cost + component.c_var * energy
        else:
            annual_cost = c_o_m

        for t in range(l):
            if t == 0:
                lcoe += ((c_invest + annual_cost) / (1 + i) ** t) / (energy / (1 + i) ** t)
            else:
                lcoe += (annual_cost / (1 + i) ** t) / (energy / (1 + i) ** t)

        print(component.name, lcoe)

        return lcoe
