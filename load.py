import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt

# TODO:
#   - Summarize load profile values if resolution is lower
#   - adjust resolution


class Load:
    """
    Class to represent loads
    """
    def __init__(self,
                 env,
                 name: str = None,
                 load_profile: pd.DataFrame = None):

        self.env = env
        self.name = name
        self.df = pd.DataFrame(columns=['P [W]'], index=self.env.time)
        self.sum = self.df['P [W]'].sum()

        if load_profile is not None:
            # Read load_profile
            self.load_profile = pd.read_csv(load_profile, sep=';', decimal=',', index_col=0)
            self.load_profile.index = pd.to_datetime(self.load_profile.index)
            # Check load profile resolution
            resolution = self.check_resolution()
            if resolution is True:
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
        else:
            self.df['P [W]'] = None

    def check_resolution(self):
        """
        Check if self.load_profile and self.env.t_step are the same time resolution
        :return: bool
        """
        lp_time_step = self.load_profile.index[1]-self.load_profile.index[0]
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
        values = []
        i_step = int(self.env.t_step / dt.timedelta(minutes=1))
        for i in range(0, len(self.load_profile), i_step):
            lp_index = self.load_profile.index
            values.append(self.load_profile.loc[lp_index[i]:lp_index[i + i_step - 1], 'P [W]'].mean())

        return values

    def fill_values(self, values: list):
        """
        Fill values in scaled_load_profile
        :param values: list
            list with values
        :return: None
        """
        for k in range(len(values)):
            self.scaled_load_profile.loc[self.scaled_load_profile.index[k], 'P [W]'] = values[k]

    def adjust_length(self, profile: pd. DataFrame):
        """
        Adjust load profile length to env.time_series
        :param profile: pd.DataFrame
            load profile to scale
        :return: None
        """
        df_index = self.df.index
        p_index = profile.index
        factor = int(len(df_index) / len(p_index))
        for i in range(factor):
            self.df.loc[df_index[len(p_index)*i]:df_index[len(p_index)*(i+1)-1], 'P [W]'] = profile['P [W]'].values
