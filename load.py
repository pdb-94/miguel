import pandas as pd


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

        if load_profile is not None:
            self.load_profile = pd.read_csv(load_profile,  sep=';', decimal=',', index_col=0)
            index = self.df.index
            lp_index = len(self.load_profile.index)
            length_diff = int(len(index) / lp_index)
            for i in range(length_diff):
                self.df.loc[index[lp_index*i]:index[lp_index*(i+1)-1], 'P [W]'] = self.load_profile['power [W]'].values
        else:
            self.df['P [W]'] = None
