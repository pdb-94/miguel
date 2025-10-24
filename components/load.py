import sys
import os
import pandas as pd
import datetime as dt
import numpy as np


class Load:
    """
    Class to represent loads
    """

    def __init__(self,
                 env,
                 name: str = None,
                 annual_consumption: float = None,
                 ref_profile: str = None,
                 load_profile: str = None):
        self.env = env
        self.name = name
        if annual_consumption is not None:
            self.annual_consumption = annual_consumption * 1000  # Wh
        else:
            self.annual_consumption = 0
        if ref_profile is not None:
            self.ref_profile = ref_profile
        else:
            self.ref_profile = None

        self.df = pd.DataFrame(columns=['P [W]'], index=self.env.time)
        self.sum = self.df['P [W]'].sum()

        if load_profile is not None:
            # Read provided load_profile
            self.load_profile = pd.read_csv(load_profile,
                                            index_col=0,
                                            header=0,
                                            sep=self.env.csv_sep,
                                            decimal=self.env.csv_decimal)
            self.original_load_profile = self.load_profile
        else:
            # Differentiate ghanaian or bdew reference load profile
            if self.ref_profile == 'hospital_ghana':
                self.load_profile = self.standard_load_profile()
            else:
                # use project-relative data file for BDEW reference
                base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
                default_bdew = os.path.join(base_dir, 'data', 'Lastprofil_Rerferenz.csv')
                self.load_profile = self.bdew_reference_load_profile(profile=self.ref_profile, file_path=default_bdew)

        self.load_profile.index = pd.to_datetime(self.load_profile.index)

        # Check if load profile resolution matches environment time resolution
        resolution = self.check_resolution()
        if resolution:
            self.adjust_length(profile=self.load_profile)
        else:
            # Create Scaled load profile
            start = dt.datetime(year=self.env.t_start.year, month=1, day=1, hour=0, minute=0)
            end = dt.datetime(year=self.env.t_start.year, month=1, day=1, hour=23, minute=45)
            res_index = pd.date_range(start=start, end=end, freq=self.env.t_step)
            self.scaled_load_profile = pd.DataFrame(columns=['P [W]'], index=res_index)
            self.scaled_load_profile.index = pd.to_datetime(self.scaled_load_profile.index)
            # Summarize and fill values based on time step
            values = self.summarize_values()
            self.fill_values(values=values)
            # Adjust scaled profile length to env.time_series
            self.adjust_length(profile=self.scaled_load_profile)

    def check_resolution(self):
        """
        Check if self.load_profile and self.env.t_step are the same time resolution
        :return: bool
        """
        lp_time_step = self.load_profile.index[1] - self.load_profile.index[0]
        return lp_time_step == self.env.t_step

    def summarize_values(self):
        """
        Summarize values based on self.env.t_step
        :return: list
            mean values
        """
        lp_time_step = (self.load_profile.index[1] - self.load_profile.index[0]) / dt.timedelta(minutes=1)
        factor = 1 if lp_time_step == 1 else 15
        lp_index = self.load_profile.index
        values = self.load_profile.groupby(np.arange(len(lp_index)) // int(self.env.i_step / factor))['P [W]'].mean().tolist()
        return values

    def fill_values(self, values: list):
        """
        Fill values in scaled_load_profile
        :param values: list
            list with values
        :return: None
        """
        self.scaled_load_profile['P [W]'] = values

    def adjust_length(self, profile: pd.DataFrame):
        """
        Adjust load profile length to env.time_series
        :param profile: pd.DataFrame
            load profile to scale
        :return: None
        """
        df_index = self.df.index
        p_index = profile.index
        factor = int(len(df_index) / len(p_index))
        # Repeat load profile according to factor
        repeated_profile = np.tile(profile['P [W]'].values, factor)
        # Assign values to df
        self.df['P [W]'] = repeated_profile[:len(self.df)]

    def standard_load_profile(self):
        """
        Build load profile from standard load profile and annual energy consumption
        :return: pd.DataFrame
            standard_load_profile
        """
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        file_path = os.path.join(base_dir, 'data', 'Lastprofil_Rerferenz.csv')

        try:
            # Load the CSV file
            s_lp = pd.read_csv(file_path, sep=';', decimal=',', encoding='latin1')

            # Verify required columns exist
            if 'time' not in s_lp.columns or 'Percentage [P/P_max]' not in s_lp.columns:
                raise ValueError("The CSV file does not contain required columns: 'time' or 'Percentage [P/P_max]'.")

            # Convert time column and set index
            s_lp['time'] = pd.to_datetime(s_lp['time'], format='%H:%M', errors='coerce')
            s_lp = s_lp.set_index('time')

            # Daily consumption and scaling
            daily_consumption = self.annual_consumption / 365  # Wh/d
            daily_sum = s_lp['Percentage [P/P_max]'].sum() * self.env.i_step / 60
            scale = daily_consumption / daily_sum if daily_sum != 0 else 0
            s_lp['P [W]'] = s_lp['Percentage [P/P_max]'] * scale

            return s_lp

        except FileNotFoundError:
            raise FileNotFoundError(f"The file {file_path} was not found.")
        except Exception as e:
            raise RuntimeError(f"Error loading standard load profile: {e}")

    def bdew_reference_load_profile(self, profile: str, file_path: str):
        """
        Build BDEW reference load profile from a CSV file
        :param profile: str
            BDEW profile identifier (e.g., 'L0')
        :param file_path: str
            Path to the CSV file containing the BDEW profiles
        :return: pd.DataFrame
            Structured load profile
        """
        if not file_path:
            raise ValueError("File path to the BDEW reference load profile CSV is required.")

        # Load the CSV file
        data = pd.read_csv(file_path, sep=self.env.csv_sep, decimal=self.env.csv_decimal, encoding='latin1')

        # Initialize DataFrame with environment time series
        df = pd.DataFrame(columns=['Season', 'Weekday', 'P [W]'], index=self.env.time_series)

        # Define weekdays (0 = Weekday, 5/6 = Weekend)
        df['Weekday'] = df.index.dayofweek
        df['Weekday'] = np.where(df['Weekday'] < 5, 0, df['Weekday'])

        # Define seasons
        month = df.index.month
        season_conditions = [month.isin(self.env.seasons[season]) for season in self.env.seasons]
        season_values = [str(season) for season in self.env.seasons.keys()]
        df['Season'] = np.select(season_conditions, season_values, default='Unknown')

        # Extract relevant profiles from the CSV
        try:
            bdew_profile = {
                'winter': {5: data[f"{profile}_winter_5"], 6: data[f"{profile}_winter_6"], 0: data[f"{profile}_winter_w"]},
                'summer': {5: data[f"{profile}_summer_5"], 6: data[f"{profile}_summer_6"], 0: data[f"{profile}_summer_w"]},
                'transition': {5: data[f"{profile}_transition_5"], 6: data[f"{profile}_transition_6"], 0: data[f"{profile}_transition_w"]},
            }
        except KeyError as e:
            raise ValueError(f"The column {e} was not found in the CSV file. Check the column names.")

        # Fill DataFrame based on season and weekday
        profiles = []
        for relative_idx, idx in enumerate(df.index):
            season = df.at[idx, 'Season']
            weekday = df.at[idx, 'Weekday']
            if season in bdew_profile and weekday in bdew_profile[season]:
                profiles.append(bdew_profile[season][weekday].iloc[relative_idx % len(bdew_profile[season][weekday])])
            else:
                # Debugging information and fallback value
                profiles.append(0)

        # Assign profiles to DataFrame
        df['P [W]'] = profiles

        # Convert to numeric and handle errors
        df['P [W]'] = pd.to_numeric(df['P [W]'], errors='coerce').fillna(0)

        # Scale based on annual energy consumption
        total = df['P [W]'].sum() * self.env.i_step / 60  # Annual consumption in kWh
        scale = self.annual_consumption / total if total > 0 else 1
        df['P [W]'] *= scale

        return df

    def retrieve_bdew_profile(self, profile: str = None, file_path: str = None):
        """
        Retrieve BDEW reference load profile from CSV file
        :param profile: str
            BDEW profile identification
        :param file_path: str
            Path to the CSV file containing the profiles (optional)
        :return: dict
            BDEW standard load profiles
        """
        # Default to project data file if not provided
        if file_path is None:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            file_path = os.path.join(base_dir, 'data', 'Lastprofil_Rerferenz.csv')

        if profile is None:
            raise ValueError("Profile identifier is required to retrieve BDEW profiles.")

        # Load the CSV file
        data = pd.read_csv(file_path, sep=';', decimal=',')

        # Extract the columns for the requested profile
        winter_5 = data[f"{profile}_winter_5"]
        winter_6 = data[f"{profile}_winter_6"]
        winter_w = data[f"{profile}_winter_w"]
        summer_5 = data[f"{profile}_summer_5"]
        summer_6 = data[f"{profile}_summer_6"]
        summer_w = data[f"{profile}_summer_w"]
        transition_5 = data[f"{profile}_transition_5"]
        transition_6 = data[f"{profile}_transition_6"]
        transition_w = data[f"{profile}_transition_w"]

        bdew_profile = {
            'winter': {5: winter_5, 6: winter_6, 0: winter_w},
            'summer': {5: summer_5, 6: summer_6, 0: summer_w},
            'transition': {5: transition_5, 6: transition_6, 0: transition_w}
        }

        return bdew_profile
