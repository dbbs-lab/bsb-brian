import brian2
from bsb import config
from bsb.config import types
from bsb.simulation.connection import ConnectionModel


@config.dynamic(attr_name="model_strategy", required=False)
class BrianConnection(ConnectionModel):
    on_pre = config.attr()
    constants = config.dict(type=types.any_())

    def create_connections(self, simdata, pre_nodes, post_nodes, cs):
        # This creates the synapses between all the neurons of the targetted
        # populations but if you want to support the full power of the BSB,
        # use `cs.load_connections().all()` (or one of the more memory friendly iterators)
        # to load the neuron to neuron connections! (If Brian supports multicomp, the CS
        # also contains which comp to which comp should be connected)
        synapses = brian2.Synapses(pre_nodes, post_nodes, on_pre=self.on_pre)
        # I just blindly replicate the tutorial here, I have no idea of the implications
        synapses.connect(**self.constants)
        return synapses
