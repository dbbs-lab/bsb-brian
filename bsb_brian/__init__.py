from bsb.simulation import SimulationBackendPlugin
from .adapter import BrianAdapter
from .simulation import BrianSimulation


__plugin__ = SimulationBackendPlugin(Simulation=BrianSimulation, Adapter=BrianAdapter)
