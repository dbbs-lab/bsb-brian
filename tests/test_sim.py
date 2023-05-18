import unittest
from bsb.config import from_file
from bsb.core import Scaffold


class TestSimulation(unittest.TestCase):
    def test_sim(self):
        cfg = from_file("./data/test.json")
        network = Scaffold(cfg)
        network.compile()
        res = network.run_simulation("test")
        print(res.block.segments[0].analogsignals)
