from bsb import config
from bsb.config import types
from bsb.simulation.simulation import Simulation
from .cell import BrianCell
from .connection import BrianConnection
from .device import BrianDevice


@config.node
class BrianSimulation(Simulation):
    """
    Configuration description of a simulation in the Brian simulator.
    """

    resolution = config.attr(type=types.float(min=0.0), default=1.0)

    cell_models = config.dict(type=BrianCell, required=True)
    connection_models = config.dict(type=BrianConnection, required=True)
    devices = config.dict(type=BrianDevice, required=True)
