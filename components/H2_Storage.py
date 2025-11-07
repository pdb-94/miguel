import pandas as pd
import datetime as dt
from components.electrolyser import Electrolyser




class H2Storage:
    """
    Class to simulate hydrogen storage in a standalone manner.
    This class manages hydrogen inflow, outflow, and storage levels without environment integration.

    1) Der Speicher wird initialisiert auf soc_min
    2) Wenn die Update Methode mit INFLOW aufgerufen wird, wird der Speicher aufgeladen und der Speicher Niveau aktualisiert
    3) Wenn die Update Methode mit Outflow aufgerufen wird, wird der Speicher entgeladen und der Speicher Niveau aktualisiert
    1) The storage is initialized at soc_min
    2) When the update method is called with INFLOW, the storage is charged and the storage level is updated
    3) When the update method is called with Outflow, the storage is discharged and the storage level is updated
    """
    def __init__(self,
                 env,
                 co2_init: float = 48,      # 48 kg/ kg H2
                 capacity: float = None,     # [kg]
                 initial_level: float = None,  # [% or absolute kg]
                 name: str = None,
                 c_invest: float = None,  # [USD]
                 c_invest_n: float = 534.94,   # [USD/kg]
                 c_op_main: float = None,  # [USD/a]
                 c_op_main_n: float = 0,    # [USD/kg]
                 c_var_n: float = 0,
                 lifetime: int = 25
                 ):
        """
        Initialize the hydrogen storage.

        :param capacity: Total storage capacity in kilograms (kg).
        :param initial_level: Initial hydrogen level in the storage (kg or fraction if <=1).
        """
        self.env = env
        self.soc_min = 0.01
        self.soc_max = 0.95
        self.name = name
        self.capacity = capacity  # Maximum storage capacity in kg
        if initial_level is not None:
            self.current_level = initial_level * capacity
        else:
            self.current_level = 0.1 * capacity  # Default: 10% initial
        self.lifetime= lifetime
        # Emissionsdaten
        self.co2_init = co2_init * self.capacity  # kg CO₂
        # Kosten
        self.invest_cost =c_invest   # Investement cost [USD]
        if c_invest is None:
           self.c_invest = c_invest_n * self.capacity
        else:
            self.c_invest = c_invest
        #Operation Cost
        self.c_op_main = c_op_main     # USD /a
        self.c_op_main_n = c_op_main_n   #USD /KG ODER kw
        if c_op_main is None:
            self.c_op_main = self.c_op_main_n * self.capacity
        else:
            self.c_op_main = c_op_main
        #variable COST
        self.c_var_n = c_var_n
        self.c_var = self.c_var_n * self.capacity
        # DataFrame to track storage levels and flows over time
        self.hstorage_df = pd.DataFrame(columns=['H2 Inflow [kg]',
                                                'H2 Outflow [kg]',
                                                'Storage Level [kg]',
                                                 'SOC [%]',
                                                 'Q[Wh]'], index= self.env.time)
        # Set initial values in dataframe
        initial_soc = self.current_level / self.capacity
        start_time = self.env.time[0]
        self.hstorage_df.at[start_time, 'Storage Level [kg]'] = self.current_level
        self.hstorage_df.at[start_time, 'SOC'] = initial_soc

        self.technical_data = {
            'Component': 'Hydrogen Storage',
            'Name': f'H2Storage_{id(self)}',  # Unique identifier for each instance
            'Capacity [kg]': self.capacity,
            'Initial Level [kg]': self.current_level,
        }

    def charge(self, clock: dt.datetime, inflow: float, el: Electrolyser):
        """
        Charge the hydrogen storage.

        :param clock: Current timestamp.
        :param inflow: Amount of hydrogen added to the storage (kg).
        """
        time_step = self.env.i_step / 60

        if inflow < 0:
            inflow = 0  # No charging if no inflow present

        if inflow == 0:
            new_level = self.current_level
        else:
            new_level = self.current_level + inflow

        if new_level > self.capacity:
            inflow = self.capacity - self.current_level  # Adjust to prevent overflow
            new_level = self.capacity

        self.current_level = new_level

        soc = (self.current_level / self.capacity)*100
        charge = 33.33 * inflow * 1000 * time_step   #[W]

        # Logging ins DataFrame
        self.hstorage_df.at[clock, 'H2 Inflow [kg]'] = inflow
        self.hstorage_df.at[clock, 'H2 Outflow [kg]'] = 0
        self.hstorage_df.at[clock, 'Storage Level [kg]'] = new_level
        self.hstorage_df.at[clock, 'SOC [%]'] = soc
        self.hstorage_df.at[clock, 'Q[Wh]'] += charge
        #self.storage_df.at[clock, 'H2 Production [kg]'] = el.df_electrolyser.at[clock, 'H2_Production [kg]']
        return

    def discharge(self, clock: dt.datetime, outflow: float):
        """
        Discharge hydrogen from the storage, respecting soc_min limit.

        :param clock: Current timestamp.
        :param outflow: Amount of hydrogen withdrawn from the storage (kg).
        """
        time_step = self.env.i_step / 60

        if outflow <= 0:
            return  # No discharge needed
        # Minimum and maximum allowed withdrawal
        min_level = self.soc_min * self.capacity  # Minimum fill level (kg)
        max_outflow = self.current_level - min_level  # Maximum withdrawable amount

        if max_outflow <= 0:
            # Storage is already at or below soc_min → no withdrawal possible
            return

        # If requested outflow greater than allowed → limit it
        if outflow > max_outflow:
            outflow = max_outflow

        # Compute new current fill level
        self.current_level -= outflow

        soc = (self.current_level / self.capacity) * 100
        discharge = 33.33 * outflow * 1000 * time_step

        # Logging in DataFrame
        self.hstorage_df.at[clock, 'H2 Inflow [kg]'] = 0
        self.hstorage_df.at[clock, 'H2 Outflow [kg]'] = outflow
        self.hstorage_df.at[clock, 'Storage Level [kg]'] = self.current_level
        self.hstorage_df.at[clock, 'SOC [%]'] = soc
        # initialize Q[Wh] if missing
        if pd.isna(self.hstorage_df.at[clock, 'Q[Wh]']):
            self.hstorage_df.at[clock, 'Q[Wh]'] = 0
        self.hstorage_df.at[clock, 'Q[Wh]'] -= discharge
        return
