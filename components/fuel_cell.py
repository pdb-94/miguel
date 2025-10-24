import pandas as pd
import datetime as dt
from scipy.interpolate import interp1d



class FuelCell:
    """
    Class to represent a Fuel Cell in the Miguel simulation.
    This class simulates the energy production and hydrogen consumption of a fuel cell.
    """

    def __init__(self, env,
                 max_power: float,
                 co2_init_per_kw: float = 24.2,
                 c_invest: float = None,
                 c_invest_n: float = 2500,  #Euro/kW
                 c_var_n: float = 0,
                 c_op_main_n: float = 0,
                 c_op_main: float = None,
                 lifetime: float= 10#Hours
                 ):
        """
       Initialize the Fuel Cell including economic and emission parameters.

    :param env: Simulation environment
    :param max_power: Max output power [kW]
    :param efficiency: Efficiency (0–1)
    :param co2_init_per_kw: Initial CO2 [kg/kW]
    :param invest_cost: CAPEX [EUR]
    :param opex_annual: Annual OPEX [EUR/year]
    :param var_cost: Variable cost per kWh [EUR/kWh]
    :param co2_opex: CO2 emission during operation [g/kWh]
        """
        self.name = f"FuelCell_{len(env.fuel_cell) + 1}"
        self.env = env  # Environment object
        self.max_power = max_power  # Maximum power output in kW
        self.lifetime= lifetime
    self.operating_hours = 0.0  # operating hours tracker

    # economic and environment data
        self.co2_init = co2_init_per_kw * (self.max_power/1000)  # [kg]
        self.invest_cost = c_invest # [US$]
        self.c_invest_n = c_invest_n  # US$/kWh
        #variable Cost
        self.c_var_n = c_var_n  # US$/kWh
        #Operation Cost
        self.c_op_main_n = c_op_main_n
        if c_op_main is None:
            self.c_op_main = self.c_op_main_n * self.max_power/ 1000
        else:
            self.c_op_main = c_op_main
        if c_invest is None:
           self.c_invest = c_invest_n * self.max_power / 1000
        else:
            self.c_invest = c_invest
        # DataFrame to store simulation data
        self.df_fc = pd.DataFrame(index=self.env.time, columns=['Power Output [W]', 'H2 Consumed [kg]'])
        self.df_fc.fillna(0, inplace=True)

        #Efficiency Curve
    df_eff = pd.read_csv("data/Fuelcell_efficiency_curve.csv", sep=',', decimal='.')
    print("Column names:", df_eff.columns.tolist())
        x = df_eff['P_rel[%]'].astype(float)
        y = df_eff['Efficiency'].astype(float)
        self.efficiency_interpolator = interp1d(x, y, kind='linear', fill_value='extrapolate')

        self.replacement_parameters = self.calc_replacements()
        self.replacement_cost = sum(self.replacement_parameters[0].values())
        self.replacement_co2 = sum(self.replacement_parameters[1].values())

    def get_efficiency(self, p_rel: float = None):
        """
        Returns the interpolated efficiency for a relative power [%].
        Defaults to 100% rated power.
        """
        if p_rel is None:
            p_rel = 100.0
    p_rel = max(0, min(p_rel, 100))  # clamp between 0 and 100 %
        return float(self.efficiency_interpolator(p_rel))

    def fc_operate(self, clock: dt.datetime, hydrogen_used: float, eff: float, power_output: float):
        """
        Logs the operation of the fuel cell based on planned H2 amount, efficiency and power.
        """
        time_step = self.env.i_step / 60
        self.operating_hours += time_step

    # Only logging and storage
        current_time = self.env.time[self.env.i_step]
        self.df_fc.at[clock, 'Power Output [W]'] = power_output
        self.df_fc.at[clock, 'H2 Consumed [kg]'] = hydrogen_used

        return power_output, hydrogen_used

    def calc_replacements(self):
        """
        Calculate energy storage replacement cost
        :return: dict
            replacement years + cost in US$
        """
        c_invest_replacement = {}
        co2_replacement = {}

        replacements = int (self.env.lifetime/ self.lifetime)
        interval = self.env.lifetime / replacements
        for year in range(int(interval), int(replacements*interval)-1, int(interval)):
            c_invest_replacement[year] = (self.c_invest_n * (self.max_power/1000)) / ((1 + self.env.d_rate) ** year)
            co2_replacement[year] = (self.co2_init  ) / ((1 + self.env.d_rate) ** year)

        return c_invest_replacement, co2_replacement




