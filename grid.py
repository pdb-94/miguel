import pandas as pd


class Grid:
    def __init__(self,
                 env,
                 name: str = None):
        self.env = env
        self.name = name

        self.df = pd.DataFrame(columns=['P [W]', 'Blackout'], index=self.env.time)
