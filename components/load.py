import sys
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
        if ref_profile is not None:
            self.ref_profile = ref_profile
        self.df = pd.DataFrame(columns=['P [W]'], index=self.env.time)
        self.sum = self.df['P [W]'].sum()
        if load_profile is not None:
            # Read load_profile
            self.load_profile = pd.read_csv(load_profile,
                                            index_col=0,
                                            header=0,
                                            sep=self.env.csv_sep,
                                            decimal=self.env.csv_decimal)
            self.original_load_profile = self.load_profile
        else:
            # Differentiate ghanaian or bdew reference load profie
            if self.ref_profile == 'hospital_ghana':
                self.load_profile = self.standard_load_profile()
            else:
                self.load_profile = self.bdew_reference_load_profile(profile=self.ref_profile)
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
        if lp_time_step == self.env.t_step:
            return True
        else:
            return False

    def summarize_values(self):
        """
        Summarize values based on self.env.t_step
        :return: list
            mean values
        """
        lp_index = self.load_profile.index
        values = self.load_profile.groupby(np.arange(len(lp_index)) // int(self.env.i_step / 15))['P [W]'].mean().tolist()

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
        # Retrieve standard load profile from database
        s_lp = pd.read_sql_query("""SELECT * from standard_load_profile""", con=self.env.database.connect)
        # Format and set index
        s_lp['time'] = pd.to_datetime(s_lp['time'], format='%H:%M')
        s_lp = s_lp.set_index('time')
        # Calculate daily demand
        daily_consumption = self.annual_consumption / 365  # Wh/d
        # Sum load percentages to calculate scale
        daily_sum = s_lp['Percentage [P/P_max]'].sum() * self.env.i_step / 60
        scale = daily_consumption / daily_sum
        # Calculate load values
        s_lp['P [W]'] = s_lp['Percentage [P/P_max]'] * scale

        return s_lp

    def bdew_reference_load_profile(self, profile: str = None):
        """
        Build BDEW reference load profile
        :param profile: str
            BDEW profile identification
        :return:
        """
        # Create dataframe with environemnet time_series
        df = pd.DataFrame(columns=['Season', 'Weekday', 'P [W]'], index=self.env.time_series)
        # Define weekday
        df['Weekday'] = df.index.dayofweek
        df['Weekday'] = np.where(df['Weekday'] < 5, 0, df['Weekday'])
        # Define season
        month = df.index.month
        season_conditions = [month.isin(self.env.seasons[season]) for season in self.env.seasons]
        season_values = list(self.env.seasons.keys())
        df['Season'] = np.select(season_conditions, season_values)
        # Retrieve BDEW profile
        bdew_profile = self.retrieve_bdew_profile(profile=profile)
        # FIll df with matching reference profile based on season and weekday
        if self.env.i_step == 15:
            day_values = df.loc[::96, 'Weekday'].values
            season_values = df.loc[::96, 'Season'].values
            profiles = [bdew_profile.get(season).get(day) for day, season in zip(day_values, season_values)]
            df['P [W]'] = np.concatenate([profile.values for profile in profiles])
        elif self.env.i_step == 60:
            day_values = df.loc[::24, 'Weekday'].values
            season_values = df.loc[::24, 'Season'].values
            profiles = [bdew_profile.get(season).get(day) for day, season in zip(day_values, season_values)]
            adjusted_profiles = [profile.rolling(4).mean().iloc[3::4].reset_index(drop=True) for profile in profiles]
            df['P [W]'] = np.concatenate([adjusted_profile.values for adjusted_profile in adjusted_profiles])
        else:
            return
        # Scale annual consumption and fill values
        total = df['P [W]'].sum() * self.env.i_step / 60  # Annual consumption in kWH - scaled to time resolution
        # print(total)
        scale = self.annual_consumption / total
        # print(df)
        df['P [W]'] = df['P [W]'] * scale

        return df

    def retrieve_bdew_profile(self, profile: str = None):
        """
        Retrieve BDEW reference load profile from miguel.db
        :param profile: str
        :return: list
            bdew standard load profiles
        """
        if profile is not None:
            winter_5 = pd.read_sql_query(f'SELECT {profile}_winter_5 from bdew_standard_load_profile',
                                         con=self.env.database.connect)
            winter_6 = pd.read_sql_query(f'SELECT {profile}_winter_6 from bdew_standard_load_profile',
                                         con=self.env.database.connect)
            winter_w = pd.read_sql_query(f'SELECT {profile}_winter_w from bdew_standard_load_profile',
                                         con=self.env.database.connect)
            summer_5 = pd.read_sql_query(f'SELECT {profile}_summer_5 from bdew_standard_load_profile',
                                         con=self.env.database.connect)
            summer_6 = pd.read_sql_query(f'SELECT {profile}_summer_6 from bdew_standard_load_profile',
                                         con=self.env.database.connect)
            summer_w = pd.read_sql_query(f'SELECT {profile}_summer_w from bdew_standard_load_profile',
                                         con=self.env.database.connect)
            transition_5 = pd.read_sql_query(f'SELECT {profile}_transition_5 from bdew_standard_load_profile',
                                             con=self.env.database.connect)
            transition_6 = pd.read_sql_query(f'SELECT {profile}_transition_6 from bdew_standard_load_profile',
                                             con=self.env.database.connect)
            transition_w = pd.read_sql_query(f'SELECT {profile}_transition_w from bdew_standard_load_profile',
                                             con=self.env.database.connect)

            bdew_profile = {'winter': {5: winter_5, 6: winter_6, 0: winter_w},
                            'summer': {5: summer_5, 6: summer_6, 0: summer_w},
                            'transition': {5: transition_5, 6: transition_6, 0: transition_w}}

            return bdew_profile
        else:
            return
