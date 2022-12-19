
class Component:
    """
    Parent class for classes PV; WindTurbine, DieselGenerator, Storage
    """
    def __init__(self,
                 env,
                 name: str = None,
                 p_n: float = 0.0,
                 c_invest: float = 0.0,
                 c_op_main: float = 0.0):
        self.env = env
        self.name = name
        self.p_n = p_n
        self.c_invest = c_invest
        self.c_op_main = c_op_main
