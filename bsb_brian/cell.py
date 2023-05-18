import brian2
import quantities
from brian2 import ms
from bsb import config
from bsb.config import types
from bsb.simulation.cell import CellModel
from bsb.simulation.parameter import Parameter


@config.node
class BrianCell(CellModel):
    equation = config.attr(required=True)
    threshold = config.attr()
    reset = config.attr()
    method = config.attr(type=types.in_(["exact"]))
    constants = config.dict(type=types.any_())
    parameters = config.list(type=Parameter)

    def create_group(self, simdata):
        n = len(simdata.placement[self])
        kwargs = {
            k: v
            for k in ("threshold", "reset", "method")
            if (v := getattr(self, k)) is not None
        }
        population = brian2.NeuronGroup(n, self.equation, **kwargs)
        self.set_constants(population)
        self.set_parameters(population, simdata)
        return population

    def set_constants(self, population):
        for k, (value, unit) in self.constants.items():
            values = [value] * len(population)
            if unit is not None:
                setattr(population, k, values * getattr(brian2, unit))
            else:
                setattr(population, k, values)
        # Note: quick hack to have exactly the same result as the Brian tutorial
        population.I[1] = 0
        population.tau[1] = 100 * brian2.ms

    def set_parameters(self, population, simdata):
        ps = simdata.placement[self]
        for param in self.parameters:
            # Calculate parameter values for all individuals in the placement set
            setattr(population, param.name, param.get_value(ps))
