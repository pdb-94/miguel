import math
import sys
import numpy as np
import pandas as pd
from lcoe.lcoe import lcoe as py_lcoe
from environment import Environment
from operation import Operator
from components.grid import Grid
from components.pv import PV
from components.windturbine import WindTurbine
from components.storage import Storage
from components.H2_Storage import H2Storage
from components.electrolyser import Electrolyser
from components.fuel_cell import FuelCell

class Evaluation:
    """
    Class to evaluate the energy system
    """

    def __init__(self,
                 env: Environment = None,
                 operator: Operator = None):
        self.env = env
        self.op = operator
        # Evaluation df
        self.evaluation_df = self.build_evaluation_df()
        # System  parameters
        self.energy_consumption_annual = self.calc_energy_consumption_annual()  # kWh
        self.peak_load = self.calc_peak_load()  # kW
        if self.env.grid_connection:
            self.grid_cost_comparison_annual = self.calc_grid_energy_annual_cost()
            self.grid_cost_comparison_lifetime = self.calc_lifetime_value(initial_value=0,
                                                                          annual_value=self.grid_cost_comparison_annual)
        else:
            self.grid_cost_comparison_annual = None
            self.grid_cost_comparison_lifetime = None

        # Components evaluation parameters
        self.pv_energy_supply = {}
        self.wt_energy_supply = {}
        self.H2_energy_supply = {}
        self.grid_energy_supply = {}
        self.storage_energy_supply = {}

        for component in self.env.re_supply:
            self.calc_component_energy_supply(component=component)
            self.calc_co2_emissions(component=component)
            self.calc_cost(component=component)
        self.calc_pv_system_flows()
        # Berechnung der Speicherenergie (inkl. H2)
        self.calc_storage_energy_supply()
        self.calc_H2_energy_supply()
        #Bewertung der Speicher (Batterie & H2-System)
        for es in self.env.storage:
            self.calc_co2_emissions(component=es)
            self.calc_cost(component=es)
        for fc in self.env.fuel_cell:
            self.calc_co2_emissions(component=fc)
            self.calc_cost(component=fc)
        for el in self.env.electrolyser:
            self.calc_co2_emissions(component=el)
            self.calc_cost(component=el)
        for hstr in self.env.H2Storage:
            self.calc_co2_emissions(component=hstr)
            self.calc_cost(component=hstr)

        self.calc_lifetime_energy_supply()
        self.calc_system_values()
        self.calc_lcoe()
        self.evaluation_df.to_csv(sys.path[1] + '/export/system_evaluation.csv',
                                  sep=self.env.csv_sep,
                                  decimal=self.env.csv_decimal)

    def run(self, export: bool = True):
    """
    Prints the main evaluation results (energy, costs, CO2)
    and optionally saves them as an Excel file.
    """
    print("✅ Evaluation completed.")

    print("\n📊 Energy flows:")
        print(self.evaluation_df[['Annual energy supply [kWh/a]', 'Lifetime energy supply [kWh]']])

    print("\n💰 Costs:")
        print(self.evaluation_df[
                  ['Investment cost [US$]', 'Annual cost [US$/a]', 'Lifetime cost [US$]', 'LCOE [US$/kWh]']])

    print("\n🌍 CO₂ emissions:")
        print(self.evaluation_df[
                  ['Initial CO2 emissions [t]', 'Annual CO2 emissions [t/a]', 'Lifetime CO2 emissions [t]']])

        if export:
            path = sys.path[1] + "/export/evaluation_summary_output.xlsx"
            self.evaluation_df.to_excel(path)
            print(f"\n💾 Results saved to: {path}")

    def build_evaluation_df(self):
        """
        Create dataframe for system evaluation
        :return: pd.DataFrame
        """
        col = ['Annual energy supply [kWh/a]', 'Lifetime energy supply [kWh]', f'Lifetime cost [US$]',
               f'Investment cost [{self.env.currency}]', f'Annual cost [US$/a]',
               f'LCOE [{self.env.currency}/kWh]', 'Lifetime CO2 emissions [t]', 'Initial CO2 emissions [t]',
               'Annual CO2 emissions [t/a]']
        evaluation_df = pd.DataFrame(columns=col)
        evaluation_df.loc['PV_to_storage'] = np.nan
        evaluation_df.loc['PV_to_electrolyser'] = np.nan
        evaluation_df.loc['PV_Total'] = np.nan

        for supply_comp in self.env.supply_components:
            evaluation_df.loc[supply_comp.name] = np.nan
        for wt in self.env.wind_turbine:
            evaluation_df.loc[f'{wt.name}_to_storage'] = np.nan
            evaluation_df.loc[f'{wt.name}_from_PV_to_electrolyser [W]'] = np.nan

        for es in self.env.storage:
                evaluation_df.loc[es.name] = np.nan
                evaluation_df.loc[es.name + '_charge'] = np.nan
                evaluation_df.loc[es.name + '_discharge'] = np.nan

        for el in self.env.electrolyser:
            evaluation_df.loc[el.name] = np.nan
        #for hstr  in self.env.H2Storage:
            #evaluation_df.loc[hstr.name] = np.nan

        for fc in self.env.fuel_cell:
            evaluation_df.loc[fc.name] = np.nan

        evaluation_df.loc['System'] = np.nan

        return evaluation_df

    def calc_energy_consumption_annual(self):
        """
        Calculate annual energy consumption
        :return: float
            energy_consumption [kWh]
        """
        energy_consumption = self.env.df['P_Res [W]'].sum() * self.env.i_step / 60 / 1000

        self.evaluation_df.loc['System', 'Annual energy supply [kWh/a]'] = int(energy_consumption)

        return energy_consumption

    def calc_grid_energy_annual_cost(self):
        """
        Calculate grid cost to meet annual consumption
        :return: float
        """
        cost = self.energy_consumption_annual * self.env.electricity_price  # US$

        return cost


    def calc_lifetime_energy_supply(self):
        """
        Calculate lifetime energy supply
        :return:
        """
    # How much energy does a component deliver (or consume) over the entire project lifetime (e.g., 20 years)?
    print("\n📊 Starting lifetime energy calculation...")
        for row in self.evaluation_df.index:
            annual_energy_supply = self.evaluation_df.loc[row, 'Annual energy supply [kWh/a]']
            if pd.isna(annual_energy_supply):
                print(f"⚠️ {row} has annual_energy_supply = NaN -> skipped")
                continue
            print(f"➤ {row}: annual = {annual_energy_supply}")
            self.evaluation_df.loc[row, 'Lifetime energy supply [kWh]'] \
                = int(self.calc_lifetime_value(initial_value=0,
                                               annual_value=annual_energy_supply))

    def calc_peak_load(self):
        """
        Calculate peak load
        :return: float
            peak load [kW]
        """
        peak_load = self.env.df['P_Res [W]'].max() / 1000

        return peak_load

    def calc_component_energy_supply(self,
                                     component: PV or WindTurbine or Grid
                                     ):
        """
        Calculate annual energy supply of energy supply components
        :param component:
        :return: None
        """
        self.n_Modul = len(self.env.pv)
        energy_total =self.calc_pv_system_flows()
        energy_Modul= energy_total/self.n_Modul

        self.evaluation_df.loc[component.name, 'Annual energy supply [kWh/a]'] = int(energy_Modul)


    def calc_pv_system_flows(self):
    """
    Calculates the energy distribution of PV production:
    PV → Load, Storage, Electrolyser, Total
    """
        i_step = self.env.i_step

    # Direct consumption (load coverage)
        load = self.op.df['Load [W]']
        pv_prod = self.op.df['PV_Production [W]']
        pv_to_load = np.minimum(load, pv_prod).sum() *(i_step / 60)/ 1000
        self.evaluation_df.loc['PV_to_load', 'Annual energy supply [kWh/a]'] = int(pv_to_load)

    # Storage
        pv_to_storage = 0
        if 'PV_to_storage [W]' in self.op.df.columns:
            pv_to_storage = self.op.df['PV_to_storage [W]'].sum() * i_step / 60 / 1000
            self.evaluation_df.loc['PV_to_storage', 'Annual energy supply [kWh/a]'] = int(pv_to_storage)

    # Electrolyser
        pv_to_el = 0
        if 'from_PV_to_electrolyser [W]' in self.op.df.columns:
            pv_to_el = self.op.df['from_PV_to_electrolyser [W]'].sum() * i_step / 60 / 1000
            self.evaluation_df.loc['PV_to_electrolyser', 'Annual energy supply [kWh/a]'] = int(pv_to_el)

    # Total
        pv_total = pv_to_load + pv_to_storage + pv_to_el
        self.evaluation_df.loc['PV_Total', 'Annual energy supply [kWh/a]'] = int(pv_total)

        return pv_total

    def calc_storage_energy_supply(self):
        """
        Calculate annual energy supply of energy storage
        :return: None
        """
        for es in self.env.storage:
            col = f'{es.name} [W]'

            # Extract charge and discharge power
            charge_vals = self.op.df[col].where(self.op.df[col] > 0, 0)
            discharge_vals = self.op.df[col].where(self.op.df[col] < 0, 0)

            # Calculate kWh
            es_charge_kWh = int(charge_vals.sum() * self.env.i_step / 60 / 1000)
            es_discharge_kWh = int(discharge_vals.sum() * self.env.i_step / 60 / 1000)

            # Store results internally
            self.storage_energy_supply[f'{es.name}_charge'] = es_charge_kWh
            self.storage_energy_supply[f'{es.name}_discharge'] = es_discharge_kWh

            # Fill evaluation table
            self.evaluation_df.loc[f'{es.name}_charge', 'Annual energy supply [kWh/a]'] = es_charge_kWh
            self.evaluation_df.loc[f'{es.name}_discharge', 'Annual energy supply [kWh/a]'] = -es_discharge_kWh
            self.evaluation_df.loc[
                es.name, 'Annual energy supply [kWh/a]'] = -es_discharge_kWh  # optional: only output counts

    def calc_H2_energy_supply(self):
        for fc in self.env.fuel_cell:
            col = fc.name + ' [W]'
            print(f"🔍 Looking for column for FuelCell: {col}")
            if col not in self.op.df.columns:
                print(f"❌ Column '{col}' missing in Operator DataFrame!")
            else:
                print(f"✅ Column '{col}' found with entries:")
                print(self.op.df[col].describe())
            fc_power = int(sum(np.where(self.op.df[col] > 0,
                                        self.op.df[col],
                                        0).tolist()) * self.env.i_step / 60 / 1000)
            self.H2_energy_supply[f'{fc.name}'] = fc_power
            self.evaluation_df.loc[fc.name, 'Annual energy supply [kWh/a]'] = fc_power
        total_power_kWh = 0

        for el in self.env.electrolyser:
            col = f"{el.name} [W]"
            if col in self.op.df.columns:
                power_sum = self.op.df[col].sum() * self.env.i_step / 60 / 1000  # kWh
                self.evaluation_df.loc[el.name, 'Annual energy supply [kWh/a]'] = power_sum
                total_power_kWh += power_sum
                print(f"⚡ {el.name} energy input: {power_sum:.2f} kWh")
            else:
                print(f"⚠️ Column {col} missing in Operator DataFrame.")


    #================================================= CO2_Calculation ===================================================#
    #==================================================================================================================#


    def calc_co2_emissions(self, component):
        """
        Calculate total CO2 emissions of component
        :param component:
        :return:
        """
        # Initial CO2 emissions
        co2_init = self.calc_co2_initial(component=component)
        # Operating CO2 emissions
        co2_annual = self.calc_co2_annual_operation(component=component)
        # Lifetime CO2 emissions
        co2_lifetime = self.calc_lifetime_value(initial_value=co2_init,
                                                annual_value=co2_annual)

        self.evaluation_df.loc[component.name, 'Lifetime CO2 emissions [t]'] = round(co2_lifetime, 3)

    def calc_co2_initial(self, component):
        """
        Calculate initial CO2 emissions
        :param component: object
        :return: None
        """
        if isinstance(component, (Storage,FuelCell)):
            co2_init = (component.co2_init+ component.replacement_co2)/1000
        elif isinstance(component, Grid):
            co2_init = 0
        else:
            co2_init = component.co2_init / 1000

        self.evaluation_df.loc[component.name, 'Initial CO2 emissions [t]'] = round(co2_init, 3)

        return co2_init

    
    def calc_co2_annual_operation(self,
                                  component):
        """
        Calculate annual CO2 emissions emitted during operation
        :param component: object
        :return: float
        """

        if isinstance(component, Grid):
            co2_annual = self.evaluation_df.loc[
                             component.name, 'Annual energy supply [kWh/a]'] * self.env.co2_grid / 1000
        else:
            co2_annual = 0
        self.evaluation_df.loc[component.name, 'Annual CO2 emissions [t/a]'] = round(co2_annual, 3)

        return co2_annual

 # =============================================== Kosten_Calculation ==================================================#
 # ====================================================================================================================#

    def calc_cost(self, component: object):
        """
        :param component:
        :return: None
        """
        # Investment cost
        investment_cost = self.calc_investment_cost(component=component)
        # Annual cost
        annual_cost = self.calc_annual_cost(component=component)
        # Lifetime cost
        lifetime_cost = self.calc_lifetime_value(initial_value=investment_cost,
                                                 annual_value=annual_cost)

        self.evaluation_df.loc[component.name, f'Lifetime cost [US$]'] = int(lifetime_cost)

    def calc_investment_cost(self,
                             component: object):
        """
        Calculate component investment cost
        :param component: object
            energy system component
        :return: float
            component investment cost
        """
        if isinstance(component, Grid):
            investment_cost = 0
        elif isinstance(component, (Storage,FuelCell)):
            investment_cost = component.c_invest + component.replacement_cost

        else:
            investment_cost = component.c_invest

        self.evaluation_df.loc[component.name, f'Investment cost [US$]'] = int(investment_cost)

        return investment_cost

    def calc_annual_cost(self,
                         component: object):
        """
        Calculate component annual cost
        :param component: object
            energy system component
        :return: float
            annual_cost
        """

        # Werte extrahieren
        if isinstance(component, H2Storage):
            annual_output = 0
        else:
            annual_output = self.evaluation_df.loc[component.name, 'Annual energy supply [kWh/a]']
        co2 = self.evaluation_df.loc[component.name, 'Annual CO2 emissions [t/a]']

        if pd.isna(annual_output) or pd.isna(co2):
            return np.nan

        co2_cost = co2 * self.env.avg_co2_price

        # Sicherstellen, dass Kostenparameter vorhanden sind
        required_attrs = ['c_op_main', 'c_var_n']
        for attr in required_attrs:
            if not hasattr(component, attr):
                return np.nan

        additional_variable_cost = annual_output * component.c_var_n

        # Jährliche Kosten berechnen
        if isinstance(component, (Storage, Electrolyser, FuelCell, H2Storage)):
            annual_cost = component.c_op_main + co2_cost + additional_variable_cost

        elif isinstance(component, Grid):
            electricity_cost = annual_output * self.env.electricity_price
            annual_cost = electricity_cost + co2_cost + additional_variable_cost

        else:  # PV, Wind
            annual_revenues = 0
            if self.env.grid_connection and self.env.feed_in:
                try:
                    annual_revenues = self.op.df[f'{component.name} Feed in [US$]'].sum()
                except KeyError:
                    print(f"⚠️ Feed-in-Daten für {component.name} fehlen.")
            annual_cost = component.c_op_main + co2_cost - annual_revenues + additional_variable_cost


        # Speichern
        self.evaluation_df.loc[component.name, 'Annual cost [US$/a]'] = round(annual_cost, 2)

        return annual_cost

        '''
        annual_output = self.evaluation_df.loc[component.name, 'Annual energy supply [kWh/a]']
        co2 = self.evaluation_df.loc[component.name, 'Annual CO2 emissions [t/a]']
        co2_cost = co2 * self.env.avg_co2_price
        if isinstance(component, Storage ):
            additional_variable_cost = annual_output * component.c_var_n
            annual_cost = component.c_op_main + co2_cost + additional_variable_cost

        elif isinstance(component, Grid):
            electricity_cost = self.evaluation_df.loc[
                                   component.name, 'Annual energy supply [kWh/a]'] * self.env.electricity_price
            additional_variable_cost = annual_output * component.c_var_n
            annual_cost = electricity_cost + co2_cost + additional_variable_cost
        elif isinstance(component, Electrolyser):
            additional_variable_cost = annual_output * component.c_var_n
            annual_cost = component.c_op_main + co2_cost + additional_variable_cost
        elif isinstance(component, FuelCell):
            additional_variable_cost = annual_output * component.c_var_n
            annual_cost =  component.c_op_main + co2_cost + additional_variable_cost
        elif isinstance (component, H2Storage):
            additional_variable_cost = annual_output * component.c_var_n
            annual_cost = component.c_op_main + co2_cost + additional_variable_cost
        else:
            if self.env.grid_connection:
                if self.env.feed_in:
                    annual_revenues = self.op.df[f'{component.name} Feed in [US$]'].sum()
                else:
                    annual_revenues = 0
            else:
                annual_revenues = 0
            additional_variable_cost = annual_output * component.c_var_n
            annual_cost = component.c_op_main + co2_cost - annual_revenues + additional_variable_cost

        self.evaluation_df.loc[component.name, f'Annual cost [US$/a]'] = int(annual_cost)

        return annual_cost
        '''
    def calc_system_values(self):
        columns = [f'Lifetime cost [US$]',
                   f'Investment cost [US$]', f'Annual cost [US$/a]',
                   'Lifetime CO2 emissions [t]', 'Initial CO2 emissions [t]', 'Annual CO2 emissions [t/a]']
        for col in columns:
            self.evaluation_df.loc['System', col] = self.evaluation_df[col].sum()

    def calc_lcoe(self):
        """
        Calculate LCOE with given parameters
        :return: float
            LCOE
        """
        df = self.evaluation_df
        rows = [x for x in df.index if "charge" not in x]
        for row in rows:
            annual_energy_supply = df.loc[row, 'Annual energy supply [kWh/a]']
            annual_cost = df.loc[row, f'Annual cost [US$/a]']
            investment_cost = df.loc[row, f'Investment cost [US$]']
            lcoe = py_lcoe(annual_output=annual_energy_supply,
                           annual_operating_cost=annual_cost,
                           capital_cost=investment_cost,
                           discount_rate=self.env.d_rate,
                           lifetime=self.env.lifetime)
            df.loc[row, f'LCOE [US$/kWh]'] = round(lcoe, 2)

 # =====================================================Tool========================================================#
# ==================================================================================================================#

    def calc_lifetime_value(self,
                            initial_value: float,
                            annual_value: float):
        """
        Calculate the net present value (discounted total) over the system lifetime.

        This method is used to evaluate quantities distributed over time such as capital expenditures,
        annual operating costs, annual energy production or emissions. It applies the user-defined
        discount rate (d_rate) and the project lifetime.

        The initial value is included in year 0. Annual values are discounted for each subsequent year
        and summed.

        :param initial_value: float
            One-time initial value at year 0 (e.g., investment cost or initial emissions)
        :param annual_value: float
            Annual value to be discounted and summed over the lifetime
        :return: float
        """
        lifetime_lifetime_value = 0
        for i in range(self.env.lifetime):
            if i == 0:
                lifetime_lifetime_value += (initial_value + annual_value) / ((1 + self.env.d_rate) ** i)
            else:
                lifetime_lifetime_value += annual_value / ((1 + self.env.d_rate) ** i)

        lifetime_lifetime_value = int(lifetime_lifetime_value)


        return lifetime_lifetime_value
