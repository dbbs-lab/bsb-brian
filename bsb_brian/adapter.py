import typing

import brian2
from bsb.simulation.adapter import SimulatorAdapter
from bsb.simulation.results import SimulationResult


# You can add Brian specific result utility here. If there's for example an idiomatic way
# to record a NeuronGroup you could add a `record_group(ng)` here.
class BrianResult(SimulationResult):
    pass


class SimulationData:
    def __init__(self, simulation):
        self.result: typing.Optional[BrianResult] = None
        # The following 3 variables are part of an undocumented interface: they need to
        # be the `cell_model`/`connection_model` keys mapped to the 0-n indexed
        # representations of the individual neurons of the population, if the simulator
        # does not accessing individuals like this, then we may need some new multiscale
        # bits in the BSB that we will need for the TVB anyway.
        self.populations = dict()
        self.connections = dict()
        self.placement = {
            model: model.get_placement_set()
            for model in simulation.cell_models.values()
        }


class BrianAdapter(SimulatorAdapter):
    def __init__(self):
        self.simdata = dict()
        self.loaded_modules = set()

    def set_communicator(self, comm):
        raise NotImplementedError("Brian does not support MPI communication.")

    def prepare(self, simulation):
        # Adapters may be asked to prepare multiple simulation objects, even from the
        # same config object, so we need a new object to store any data related to the
        # simulation, that's `simdata`. Other consumers can inspect and modify this data.
        self.simdata[simulation] = simdata = SimulationData(simulation)
        try:
            simdata.result = SimulationResult(simulation)

            self.create_neuron_groups(simulation)
            self.create_synapses(simulation)
            self.create_devices(simulation)
            return self.simdata[simulation]
        except Exception:
            # If there's any preparation errors, we clean up the simdata.
            del self.simdata[simulation]
            raise

    def run(self, simulation):
        if simulation not in self.simdata:
            raise RuntimeError("Can't run unprepared simulation")
        simdata = self.simdata[simulation]

        brian2.run(simulation.duration * brian2.ms)

        return simdata.result

    def create_neuron_groups(self, simulation):
        """
        Create a population of nodes in the NEST simulator based on the cell model
        configurations.
        """
        # This function you can probably keep as is
        simdata = self.simdata[simulation]
        for cell_model in simulation.cell_models.values():
            simdata.populations[cell_model] = cell_model.create_group(simdata)

    def create_synapses(self, simulation):
        """
        Connect the cells in NEST according to the connection model configurations
        """
        # This function you can probably keep as is, it fetches the data that you usually
        # need to form the regular pre-to-post synaptic synapses.
        simdata = self.simdata[simulation]
        for connection_model in simulation.connection_models.values():
            cs = simulation.scaffold.get_connectivity_set(connection_model.name)
            try:
                pre_nodes = simdata.populations[simulation.get_model_of(cs.pre_type)]
            except KeyError:
                raise RuntimeError(f"No model found for {cs.pre_type}")
            try:
                post_nodes = simdata.populations[simulation.get_model_of(cs.post_type)]
            except KeyError:
                raise RuntimeError(f"No model found for {cs.post_type}")
            try:
                simdata.connections[
                    connection_model
                ] = connection_model.create_connections(
                    simdata, pre_nodes, post_nodes, cs
                )
            except Exception as e:
                raise RuntimeError(f"{connection_model} error during connect.")

    def create_devices(self, simulation):
        # This function you can probably keep as is
        simdata = self.simdata[simulation]
        for device_model in simulation.devices.values():
            device_model.implement(self, simulation, simdata)
