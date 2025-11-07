import sys
import numpy as np
import datetime as dt
import pandas as pd
from pathlib import Path
# MiGUEL modules
from environment import Environment
from components.pv import PV
from components.windturbine import WindTurbine
from components.storage import Storage
from components.grid import Grid
from components.electrolyser import Electrolyser
from components.fuel_cell import FuelCell
from components.H2_Storage import H2Storage
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
        self.dispatch_finished = False
        self.dispatch()
        self.export_data()

    ''' Basic Functions'''

    def build_df(self):
        """
        Assign columns to pd.DataFrame
        :return: pd.DataFrame
            DataFrame with component columns
        """
        df = pd.DataFrame(columns=['Load [W]', 'P_Res [W]','PV_Production [W]'],
                          index=self.env.time)
        df['Load [W]'] = self.env.df['P_Res [W]'].round(2)
        df['P_Res [W]'] = self.env.df['P_Res [W]'].round(2)
        df['PV_Production [W]'] = self.env.df['PV total power [W]']

        if self.env.grid_connection:
            if self.env.blackout:
                df['Blackout'] = self.env.df['Blackout']
        for pv in self.env.pv:
            pv_col = f'{pv.name} [W]'
            df[pv_col] = 0
            df[f'{pv.name} production [W]'] = pv.df['P [W]']
        for wt in self.env.wind_turbine:
            wt_col = f'{wt.name} [W]'
            df[wt_col] = 0
            df[f'{wt.name} production [W]'] = wt.df['P [W]']
        for es in self.env.storage:
            es_col = f'{es.name} [W]'
            df[es_col] = 0
            df[f'{es.name}_capacity [Wh]'] = np.nan
        for el in self.env.electrolyser:
            el_col = f'{el.name} [W]'
            df[el_col] = 0
            df[f'{el.name} power [W]'] = el.df_electrolyser['P[W]']
        for hstr in self.env.H2Storage:
            hstr_col = f'{hstr.name} [W]'
            df[hstr_col] = 0
            df[f'{hstr.name}: H2 Outflow [kg]'] = hstr.hstorage_df['H2 Outflow [kg]']
            df[f'{hstr.name}: H2 Inflow [kg]'] = hstr.hstorage_df['H2 Inflow [kg]']
            df[f'{hstr.name} _Storage Level [kg]'] = hstr.hstorage_df['Storage Level [kg]']
        for fc in self.env.fuel_cell:
            fc_col = f'{fc.name} [W]'
            df[fc_col] = 0
            df[f'{fc.name} Power[W]'] = fc.df_fc['Power Output [W]']

        if self.env.grid is not None:  # sicherstellen dass das Grid nur dann in DF AAUFGENOMMEN WIRD;Wenn ein Netz existiert
            grid_col = f'{self.env.grid.name} [W]'
            df[grid_col] = 0


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
        print(f"DEBUG: Dispatch started")
        processed_times = set()

        # Time step iteration
        for i,clock in enumerate(self.df.index):
            prev_clock = self.df.index[i - 1] if i > 0 else clock
            # Priority 1: RE self supply
            for component in env.re_supply:

                self.re_self_supply(clock=clock,
                                    component=component)
                # Initialize remains separately
            pv_remain = sum(self.df.at[clock, f'{pv.name} remain [W]'] for pv in env.pv)
            wt_remain = sum(self.df.at[clock, f'{wt.name} remain [W]'] for wt in env.wind_turbine)
            total_remain = pv_remain + wt_remain

            self.df.at[clock, 'P_Remain_total [W]'] = total_remain

            # Priority 2: Charge Storage from RE
            for es in env.storage:

                pv_remain, wt_remain = self.re_charge(clock, es, pv_power=pv_remain, wt_power=wt_remain)

            # Priority 3: Betrieb Electrolyser
            h2_produced = 0
            for h2_storage in env.H2Storage:
                # Check if storage is full (SOC [%] from previous timestep)
                h2_full = h2_storage.hstorage_df.at[prev_clock, 'SOC [%]'] >= 100

                if h2_full:
                    # Kein Betrieb, aber Werte im Elektrolyseur-DataFrame setzen
                    for el in env.electrolyser:
                        self.df.at[clock, f'{el.name} [W]'] = 0
                        self.df.at[clock, f'{el.name} [%]'] = 0
                        self.df.at[clock, f'{el.name}_Hydrogen [kg]'] = 0

                else:
                    # Nur wenn Speicher nicht voll ist → Elektrolyseur betreiben
                    for el in env.electrolyser:
                        pv_remain, wt_remain = self.electrolyser_operate(clock=clock,
                                                                         el=el,pv_power= pv_remain,
                                                                         wt_power=wt_remain)

                        h2_produced += el.df_electrolyser.at[clock, 'H2_Production [kg]']

                # Store produced hydrogen in H2 storage
                #for  h2_storage in env.H2Storage:
                self.H2_charge(clock=clock, hstr=h2_storage, inflow=h2_produced, el=el)

            for fc in env.fuel_cell:
                if self.df.at[clock,'P_Res [W]'] == 0.0:
                   self.df.at[clock, f'{fc.name} [W]'] = 0

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

        if self.env.feed_in:
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
        self.dispatch_finished = True

        cols = []
        for pv in self.env.pv:
            cols.append(f'{pv.name}')

        self.export_core_data()

        #self.plot_daily_system_behavior(day='2022-06-01')
        #self.plot_daily_system_behavior_interactive(day='2022-07-01')


    def check_dispatch(self):
        """
        Check if all load is covered with current system components
        :return: None
        """
        power_sink = {}  # speichert die nicht gedeckte Leistung
        for clock in self.df.index:
            if self.df.at[clock, 'P_Res [W]'] > 0:
                power_sink[clock] = self.df.at[clock, 'P_Res [W]']

        power_sink_df = pd.DataFrame(power_sink.items(),
                                     columns=['Time', 'P [W]'])

        power_sink_df = power_sink_df.set_index('Time')
        power_sink_df = power_sink_df.round(2)


        return power_sink_df  # die Werte werden in einer DF gegeben mit nicht gedeckte leistung

    def stable_grid(self,
                    clock: dt.datetime):
        """
        Dispatch strategy from stable grid connection
            Stable grid connection:
                3) Cover residual load from Storage
                4) Cover residual Load from Fuelcell
                5) Cover residual load from Grid
        :param clock: dt.datetime
            time stamp
        :return: None
        """
        env = self.env
        for es in env.storage:
            if self.df.at[clock, 'P_Res [W]'] > 0:
                power = self.df.at[clock, 'P_Res [W]']

                discharge_power = es.discharge(clock=clock,
                                               power=power)
                self.df.at[clock, f'{es.name} [W]'] += float(discharge_power)
                self.df.at[clock, 'P_Res [W]'] += float(discharge_power)
        # Priority 4: Cover load from grid
        if self.env.grid_connection:
            self.grid_profile(clock=clock)

    def unstable_grid(self,
                      clock: dt.datetime):
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
        if not env.df.at[clock, 'Blackout']:
            self.grid_profile(clock=clock)
        else:
            for es in env.storage:
                if self.df.at[clock, 'P_Res [W]'] > 0:
                    power = self.df.at[clock, 'P_Res [W]']
                    discharge_power = es.discharge(clock=clock,
                                                   power=power)
                    self.df.at[clock, f'{es.name} [W]'] += discharge_power
                    self.df.at[clock, 'P_Res [W]'] += discharge_power
            for fc in env.fuel_cell:
                self.re_fc_operate(clock=clock,
                                fc= fc)

    def off_grid(self,
                 clock: dt.datetime):
        """
        Dispatch strategy for Off-grid systems


        :param clock: dt.datetime
            time stamp
        :return: None
        """
        env = self.env
        p_res = self.df.at[clock, 'P_Res [W]']
        t_step = self.env.i_step

        # Check Energy storage parameters
        storage_power = {}
        storage_capacity = {}

        # discharge storage
        for es in env.storage:
            storage_power[es.name] = es.p_n
            storage_capacity[es.name] = (es.df.at[clock, 'Q [Wh]'] - es.soc_min * es.c) * t_step/ 60

        #power_sum = sum(storage_power.values())
        #capacity_sum = sum(storage_capacity.values())
        if p_res == 0:
            return
    # If residual load remains after storage discharge, use FuelCell
        if p_res >0:
            #if es.df.at[clock , 'SOC'] > es.soc_min:
                # Discharge storage
            for es in env.storage:
                power = self.df.at[clock, 'P_Res [W]']
                discharge_power = es.discharge(clock=clock, power=power)
                self.df.at[clock, f'{es.name} [W]'] += discharge_power
                #self.df.at[clock, 'P_Res [W]'] += discharge_power
                p_res += discharge_power
        # Wenn nach Speicherentladung noch Restlast besteht, FuelCell nutzen
        if p_res > 0:
            for fc in env.fuel_cell:
                for hstr in env.H2Storage:
                    fc_power = self.re_fc_operate(clock=clock,
                                                power=p_res,
                                                hstr=hstr,
                                                fc=fc)
                    self.df.at[clock, f'{fc.name} [W]'] = fc_power
                    p_res -= fc_power
        else:
            for fc in env.fuel_cell:
                self.df.at[clock, f'{fc.name} [W]'] = 0

        self.df.at[clock, 'P_Res [W]'] = p_res

        # Sicherheitsprüfung gegen negative Werte
        if self.df.at[clock, 'P_Res [W]'] < 0:
            self.df.at[clock, 'P_Res [W]'] = 0


    def feed_in(self,
                component: PV or WindTurbine):
        """
        Calculate RE feed-in power and revenues
        :param component: PV/WindTurbine
        :return: None
        """
        if self.env.grid_connection is False:
            pass
        else:
            self.df[f'{component.name} Feed in [W]'] = self.df[f'{component.name} remain [W]']
            if isinstance(component, PV):
                self.df[f'{component.name} Feed in [{self.env.currency}]'] \
                    = self.df[
                          f'{component.name} Feed in [W]'] * self.env.i_step / 60 / 1000 * self.env.pv_feed_in_tariff
            elif isinstance(component, WindTurbine):
                self.df[f'{component.name} Feed in [{self.env.currency}]'] \
                    = self.df[
                          f'{component.name} Feed in [W]'] * self.env.i_step / 60 / 1000 * self.env.wt_feed_in_tariff

    def re_self_supply(self,
                       clock: dt.datetime,
                       component: PV or WindTurbine):
        """
        Calculate re self-consumption
        :param clock: dt.datetime
             time stamp
        :param component: PV/Windturbine
            RE component
        :return: None
        """


        df = self.df

        df.at[clock, f'{component.name} [W]'] = np.where(
            df.at[clock, 'P_Res [W]'] > component.df.at[clock, 'P [W]'],
            component.df.at[clock, 'P [W]'], df.at[clock, 'P_Res [W]'])
        df.at[clock, f'{component.name} [W]'] = np.where(
            df.at[clock, f'{component.name} [W]'] < 0, 0, df.at[clock, f'{component.name} [W]'])
        df.at[clock, f'{component.name} remain [W]'] = np.where(
           component.df.at[clock, 'P [W]'] - df.at[clock, 'P_Res [W]'] < 0,
            0, component.df.at[clock, 'P [W]'] - df.at[clock, 'P_Res [W]'])

        df.at[clock, 'P_Res [W]'] -= df.at[clock, f'{component.name} [W]']
        if df.at[clock, 'P_Res [W]'] < 0:
            df.at[clock, 'P_Res [W]'] = 0

    def re_charge(self,
                  clock: dt.datetime,
                  es: Storage,
                  pv_power,
                  wt_power):
        """
        :param clock:
        :param es:
        :param remain_power:
        :return:
        """
        '''
        if clock == self.df.index[0]:
            es.df.at[clock, 'P [W]'] = 0
            es.df.at[clock, 'SOC'] = es.soc
            es.df.at[clock, 'Q [Wh]'] = es.soc * es.c
        # Charge storage
        #charge_power = es.charge(clock=clock, power=remain_power)
        if pv_power > es.p_n:
            charge_power_pv =es.charge(clock=clock, power=es.p_n)
            charge_power_wt=0
            self.df.at[clock, f'{es.name}_from_PV_[W]'] = charge_power_pv
        else:
            charge_power_pv=es.charge(clock=clock, power=pv_power)
            if wt_power>0:
                charge_power_wt=es.p_n-charge_power_pv

        if es.q_remain ==0:
            if wt_power == 0:
                charge_from_wt= 0

        self.df.at[clock, f'{es.name} [W]'] = charge_power

        self.df.at[clock, f'{es.name} soc'] = es.df.at[clock, 'SOC']

        return charge_power
        '''

        if clock == self.df.index[0]:
            es.df.at[clock, 'P [W]'] = 0
            es.df.at[clock, 'SOC'] = es.soc
            es.df.at[clock, 'Q [Wh]'] = es.soc * es.c

        t_step = self.env.i_step
        max_power = es.p_n

    # === Step 1: Try charging from PV ===
        power_pv_input = min(pv_power, max_power)
        power_used_pv = es.charge(clock=clock, power=power_pv_input)

        pv_power -= power_used_pv
        remaining_power = max_power - power_used_pv

    # === Step 2: If storage can still accept, feed wind ===
        power_used_wt = 0
        if remaining_power > 0 and wt_power > 0:
            power_wt_input = min(wt_power, remaining_power)
            power_used_wt = es.charge(clock=clock, power=power_wt_input)
            wt_power -= power_used_wt

        # === Tracking in DataFrame ===
        self.df.at[clock, 'PV_to_storage [W]'] = power_used_pv
        self.df.at[clock, 'WT_to_storage[W]'] = power_used_wt
        self.df.at[clock, f'{es.name} [W]'] = power_used_pv + power_used_wt
        self.df.at[clock, f'{es.name} soc'] = es.df.at[clock, 'SOC']

        return pv_power, wt_power


    def grid_profile(self,
                     clock: dt.datetime):
        """
        Cover load from power grid
        :param clock: dt.datetime
            time stamp
        :return: None
        """
        df = self.df
        print("Calling grid profile")
        grid = self.env.grid.name
        df.at[clock, f'{grid} [W]'] = self.df.at[clock, 'P_Res [W]']
        df.at[clock, 'P_Res [W]'] = 0

    def export_data(self):
        """
        Export data after simulation
        :return: None
        """
        sep = self.env.csv_sep
        decimal = self.env.csv_decimal
        root = sys.path[1]
        Path(f'{sys.path[1]}/export').mkdir(parents=True, exist_ok=True)
        self.df.to_csv(root + '/export/operator.csv', sep=sep, decimal=decimal)
        self.env.weather_data[0].to_csv(f'{root}/export/weather_data.csv', sep=sep, decimal=decimal)
        self.env.wt_weather_data.to_csv(f'{root}/export/wt_weather_data.csv', sep=sep, decimal=decimal)
        self.env.monthly_weather_data.to_csv(f'{root}/export/monthly_weather_data.csv', sep=sep, decimal=decimal)

    def electrolyser_operate(self, clock: dt.datetime,
                             el: Electrolyser,
                             pv_power, wt_power):

        """
        :param clock:
        :param el:
        :param power:
        :return:
        """
        power_needed = el.p_n

        # === 1. Zuerst PV nutzen ===
        power_from_pv = min(pv_power, power_needed)
        power_needed -= power_from_pv

        # === 2. Dann Wind nutzen (falls nötig) ===
        power_from_wt = min(wt_power, power_needed)
        power_needed -= power_from_wt

        # === 3. Gesamteingangsleistung setzen ===
        total_power = power_from_pv + power_from_wt
        el.run(clock=clock, power=total_power)

        # === 4. Tracking im Operator-DataFrame ===
        self.df.at[clock, 'from_PV_to_electrolyser [W]'] = power_from_pv
        self.df.at[clock, 'from_WT_to_electrolyser [W]'] = power_from_wt
        self.df.at[clock, f'{el.name}_Input_Power [W]'] = total_power
        self.df.at[clock, f'{el.name} [W]'] = el.df_electrolyser.at[clock, 'P[W]']
        self.df.at[clock, f'{el.name} [%]'] = el.df_electrolyser.at[clock, 'P[%]']
        self.df.at[clock, f'{el.name}_Hydrogen [kg]'] = el.df_electrolyser.at[clock, 'H2_Production [kg]']
        self.df.at[clock, f'{el.name} Efficiency [%]']= el.df_electrolyser.at[clock, 'Efficiency'] *100

        return pv_power, wt_power

    def H2_charge(self, clock: dt.datetime, hstr: H2Storage, inflow: float, el= Electrolyser):

        env = self.env

        index = env.H2Storage.index(hstr)
        #self.df.at[clock, f'{hstr.name} level [kg]'] = 0.0

        if clock == self.df.index[0]:

            if index == 0:
                # Set values for first time step
                hstr.hstorage_df.at[clock, 'Storage Level [kg]'] = 0.5 * hstr.capacity
                hstr.hstorage_df.at[clock, 'SOC'] = 0.5    # Der Speicher startet mit der Hälfte der Kapazität
                #hstr.hstorage_df.at[clock, 'Q [Wh]'] =

        hstr.charge(clock=clock, inflow=inflow, el=el)

        self.df.at[clock, f'{hstr.name} [W]'] = hstr.hstorage_df.at[clock, 'Q[Wh]']
        self.df.at[clock, f'{hstr.name} SOC[%]'] = hstr.hstorage_df.at[clock, 'SOC']
        self.df.at[clock, f'{hstr.name} level [kg]'] = hstr.hstorage_df.at[clock,'Storage Level [kg]']

        return

    def re_fc_operate(self,
                      clock: dt.datetime,
                      fc:FuelCell,
                      hstr: H2Storage,
                      power: float):

        t_step = self.env.i_step/60
        print(f"Timestep:{t_step}")
        fc_power = min(power, fc.max_power)

        # [kg] Berechnung der notwendigen Wasserstoffsmenge
        fc_efficiency = fc.get_efficiency(p_rel=(fc_power / fc.max_power) * 100)
        print(f"efficiency in re_fc_operate {fc_efficiency}")
        required_Hydrogen = fc_power / (33.33*1000 * fc_efficiency)

        # verfügbare Wasserstoff abrufen
        available_h2 = hstr.hstorage_df.at[clock, 'Storage Level [kg]']-(hstr.soc_min*hstr.capacity)
        #used_Hydrogen = min(required_Hydrogen, available_h2)

        if required_Hydrogen < available_h2:
            used_Hydrogen=required_Hydrogen
        else:
            # ITERATIV berechne reduzierte Leistung passend zu verfügbarem H₂
            used_Hydrogen = available_h2
            for _ in range(10):  # max 10 iterations
                fc_power = (used_Hydrogen * 33.33 * 1000 * fc_efficiency)/t_step
                p_rel = (fc_power / fc.max_power) * 100
                eff_new = fc.get_efficiency(p_rel)
                if abs(fc_efficiency - eff_new) < 1e-4:
                    break
                fc_efficiency = eff_new
            else:
                print(f"[WARN] FC @ {clock}: Iteration did not converge. η ≈ {fc_efficiency:.4f}")
        # Calculate actual delivered power and hydrogen consumption
        # Protect against non-positive hydrogen availability
        if used_Hydrogen <= 0 or fc_efficiency <= 0:
            power_generated = 0.0
            hydrogen_consumed = 0.0
            fc_power = 0.0
        else:
            power_generated, hydrogen_consumed = fc.fc_operate(clock=clock,
                                                               hydrogen_used=used_Hydrogen,
                                                               eff=fc_efficiency,
                                                               power_output=fc_power)

        # Update DataFrame and H2 storage
        self.df.at[clock, f'{fc.name} [W]'] = power_generated   # Umrechnung in Watt
        try:
            self.df.at[clock, 'P_Res [W]'] -= power_generated
        except Exception:
            pass

        # Aktualisieren des H2-Speichers nach Nutzung
        try:
            hstr.discharge(clock=clock, outflow=hydrogen_consumed)
            self.df.at[clock, f'{hstr.name} level [kg]'] = hstr.hstorage_df.at[clock, 'Storage Level [kg]']
            self.df.at[clock, 'H2-SOC [%]'] = hstr.hstorage_df.at[clock, 'SOC [%]']
        except Exception:
            # If discharge/update fails, continue without raising to keep simulation progressing
            pass

        return power_generated

    def export_core_data(self):
        export_dir = Path(f'{sys.path[1]}/export')
        export_dir.mkdir(parents=True, exist_ok=True)

        timestamp = dt.datetime.now().strftime('%Y%m%d_%H%M')
        core_file = export_dir / f'core_dispatch_{timestamp}.xlsx'

        # Wichtige Spalten auswählen
        core_columns = [
            'Load [W]',
            'P_Res [W]',
            'PV_Production [W]',
            'P_Remain_total [W]',
            'ES_1 [W]',
            'ES_1 soc',
            'Electrolyser_1 [W]',
            'Electrolyser_1 [%]',
            'Electrolyser_1 Efficiency[ %]',
            'Electrolyser_1_Hydrogen [kg]',
            'H2_Storage 1 level [kg]',
            'FuelCell_1 [W]'
        ]
        core_columns_existing = [col for col in core_columns if col in self.df.columns]
        core_df = self.df[core_columns_existing].copy()

        core_df.to_excel(core_file)
        print(f"✅ Core data export completed: {core_file}")


    def plot_daily_system_behavior(self, day=None):
        df = self.df.copy()

        # Falls kein spezifischer Tag angegeben wurde, den ersten Tag verwenden
        if day is None:
            start_date = df.index.min().normalize()
        else:
            start_date = pd.to_datetime(day).normalize()

        end_date = start_date + pd.Timedelta(days=1)

        # Tagesdaten herausfiltern
        df_day = df.loc[start_date:end_date]

        # Plot erstellen
        plt.figure(figsize=(16, 8))
        plt.plot(df_day.index, df_day['Load [W]'], label='Load [W]')
        plt.plot(df_day.index, df_day['PV_Production [W]'], label='PV production [W]')
        if 'ES_1 [W]' in df_day.columns:
            plt.plot(df_day.index, df_day['ES_1 [W]'], label='Battery [W]')
        if 'Electrolyser_1 [W]' in df_day.columns:
            plt.plot(df_day.index, df_day['Electrolyser_1 [W]'], label='Electrolyser [W]')
            if 'H2_Storage level [kg]' in df_day.columns:
                plt.plot(df_day.index, df_day['H2_Storage level [kg]'] * 1000, label='H2 storage [g]')
        if 'FuelCell_2 [W]' in df_day.columns:
            plt.plot(df_day.index, df_day['FuelCell_2 [W]'], label='FuelCell [W]')

        plt.title(f'System behavior on {start_date.date()}')
        plt.xlabel('Time')
        plt.ylabel('Power / Quantity')
        plt.legend(loc='upper left')
        plt.grid(True)
        plt.tight_layout()
        plt.show()



    def plot_daily_system_behavior_interactive(self, day=None):

        df = self.df.copy()

        if day is None:
            start_date = df.index.min().normalize()
        else:
            start_date = pd.to_datetime(day).normalize()

        end_date = start_date + pd.Timedelta(days=1)
        df_day = df.loc[start_date:end_date]

        fig = go.Figure()

        fig.add_trace(go.Scatter(x=df_day.index, y=df_day['Load [W]'],
                     mode='lines', name='Load [W]', line=dict(color='black')))
        fig.add_trace(go.Scatter(x=df_day.index, y=df_day['PV_Production [W]'],
                     mode='lines', name='PV production [W]', line=dict(color='orange')))

        if 'ES_1 [W]' in df_day.columns:
            fig.add_trace(go.Scatter(x=df_day.index, y=df_day['ES_1 [W]'],
                                     mode='lines', name='Battery [W]', line=dict(color='blue', dash='dot')))

        if 'Electrolyser_1 [W]' in df_day.columns:
            fig.add_trace(go.Scatter(x=df_day.index, y=df_day['Electrolyser_1 [W]'],
                                     mode='lines', name='Electrolyser [W]', line=dict(color='green', dash='dot')))
            if 'FuelCell_2 [W]' in df_day.columns:
                fig.add_trace(go.Scatter(x=df_day.index, y=df_day['FuelCell_2 [W]'],
                                         mode='lines', name='FuelCell [W]', line=dict(color='purple', dash='dash')))

        fig.update_layout(
            title=f'Interactive system behavior on {start_date.date()} (standard view)',
            xaxis_title='Time',
            yaxis_title='Power [W]',
            template='plotly_white',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        fig.show()



















