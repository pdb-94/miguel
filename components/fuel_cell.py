import pandas as pd
import datetime as dt
from scipy.interpolate import interp1d
import os


class FuelCell:
    """
    Class to represent a Fuel Cell in the MiGUEL simulation.
    Simulates energy production and hydrogen consumption of a fuel cell.
    """

    def __init__(self, env,
                 max_power: float,
                 co2_init_per_kw: float = 24.2,
                 c_invest: float = None,
                 c_invest_n: float = 2500,  # USD/kW
                 c_var_n: float = 0,
                 c_op_main_n: float = 0,
                 c_op_main: float = None,
                 lifetime: float = 10
                 ):
        """Initialize the Fuel Cell including economic and emission parameters.

        :param env: Simulation environment
        :param max_power: Max output power [kW]
        :param co2_init_per_kw: Initial CO2 [kg/kW]
        :param c_invest: CAPEX absolute [USD]
        :param c_invest_n: specific CAPEX [USD/kW]
        :param c_op_main: annual OPEX absolute [USD/a]
        :param c_op_main_n: specific OPEX [USD/kW/a]
        :param lifetime: lifetime in years
        """
        self.name = f"FuelCell_{len(env.fuel_cell) + 1 if hasattr(env, 'fuel_cell') else '1'}"
        self.env = env
        self.max_power = max_power  # kW
        self.lifetime = lifetime
        self.operating_hours = 0.0

        # economic and environment data
        self.co2_init = co2_init_per_kw * (self.max_power)  # kg (per kW * kW)
        self.invest_cost = c_invest
        self.c_invest_n = c_invest_n
        self.c_var_n = c_var_n
        self.c_op_main_n = c_op_main_n

        if c_op_main is None:
            self.c_op_main = self.c_op_main_n * (self.max_power)
        else:
            self.c_op_main = c_op_main

        if c_invest is None:
            self.c_invest = self.c_invest_n * (self.max_power)
        else:
            self.c_invest = c_invest

        # DataFrame to store simulation data
        self.df_fc = pd.DataFrame(index=self.env.time, columns=['Power Output [W]', 'H2 Consumed [kg]'])
        self.df_fc.fillna(0, inplace=True)

        # Efficiency interpolator
        eff_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), 'data', 'Fuelcell_efficiency_curve.csv')
        try:
            df_eff = pd.read_csv(eff_path, sep=',', decimal='.')
            x = df_eff['P_rel[%]'].astype(float)
            y = df_eff['Efficiency'].astype(float)
            self.efficiency_interpolator = interp1d(x, y, kind='linear', fill_value='extrapolate')
        except Exception:
            # If efficiency curve not available, assume constant efficiency 50%
            self.efficiency_interpolator = lambda p: 0.5

        self.replacement_parameters = self.calc_replacements()
        self.replacement_cost = sum(self.replacement_parameters[0].values())
        self.replacement_co2 = sum(self.replacement_parameters[1].values())

    def get_efficiency(self, p_rel: float = None):
        """Returns the interpolated efficiency for a relative power [%]. Defaults to 100% rated power."""
        if p_rel is None:
            p_rel = 100.0
        p_rel = max(0, min(p_rel, 100))  # clamp between 0 and 100 %
        try:
            return float(self.efficiency_interpolator(p_rel))
        except Exception:
            return float(self.efficiency_interpolator(p_rel)) if callable(self.efficiency_interpolator) else 0.5

    def fc_operate(self, clock: dt.datetime, hydrogen_used: float, eff: float, power_output: float):
        """Logs the operation of the fuel cell based on planned H2 amount, efficiency and power."""
        time_step = self.env.i_step / 60
        self.operating_hours += time_step

        # Logging and storage
        self.df_fc.at[clock, 'Power Output [W]'] = power_output
        self.df_fc.at[clock, 'H2 Consumed [kg]'] = hydrogen_used

        return power_output, hydrogen_used

    def calc_replacements(self):
        """Calculate fuel cell replacement cost and CO2 over project life."""
        c_invest_replacement = {}
        co2_replacement = {}

        replacements = int(self.env.lifetime / self.lifetime) if self.lifetime > 0 else 0
        if replacements <= 0:
            return c_invest_replacement, co2_replacement
        interval = self.env.lifetime / replacements
        for year in range(int(interval), int(replacements * interval) + 1, int(interval)):
            c_invest_replacement[year] = (self.c_invest_n * (self.max_power)) / ((1 + self.env.d_rate) ** year)
            co2_replacement[year] = (self.co2_init) / ((1 + self.env.d_rate) ** year)

        return c_invest_replacement, co2_replacement




