import brian2
from bsb import config
from bsb.simulation.device import DeviceModel
from bsb.simulation.targetting import Targetting
from neo import AnalogSignal
from quantities import ms


# `classmap_entry = None` disables this abstract device from being used, only its child
# classes are valid options
@config.dynamic(
    attr_name="device", auto_classmap=True, required=True, classmap_entry=None
)
class BrianDevice(DeviceModel):
    targetting = config.attr(type=Targetting, default={"strategy": "all"})

    # Here is an abstract method `implement` that each type of device should implement


@config.node
class StateMonitor(BrianDevice, classmap_entry="state_monitor"):
    monitor = config.attr()

    def implement(self, adapter, simulation, simdata):
        targets = self.targetting.get_targets(adapter, simulation, simdata)
        for model, population in targets.items():
            sm = brian2.StateMonitor(population, self.monitor, record=True)

            def record_sm(segment):
                recorded = getattr(sm, self.monitor)
                for i, signal in enumerate(recorded):
                    analog_signal = AnalogSignal(
                        signal,
                        units="V",
                        sampling_rate=1 / ms,
                        cell_id=i,
                        population=model.name,
                    )
                    segment.analogsignals.append(analog_signal)

            simdata.result.create_recorder(record_sm)


@config.node
class VoltageRecorder(StateMonitor, classmap_entry="voltage_recorder"):
    # `provide` provides a fixed value and removes the configurability of a parent attr
    monitor = config.provide("v")

    # Other than that a voltage recorder seems identical to a state monitor!
