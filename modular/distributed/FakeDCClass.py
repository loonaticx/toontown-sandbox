"""
FakeDCClass: Headless blackhole-tunnel for DO sendUpdate calls

Basically the equivalent of /dev/null; if a DO tries to send a sendUpdate, ensure that this is defined beforehand:
from tools.headless.distributed import NoDCClass
DistributedObjectClass.dclass = NoDCClass.NoDCClass()

"""


class FakeDatagram:
    def __init__(self):
        self.length = 0  # FREAK OUT THE NONEXISTENT SERVER

    def getLength(self):
        return self.length

class FakeDCClass():
    def __init__(self):
        pass

    def clientFormatUpdate(self, *args, **kwargs):
        """
        :return: A "FakeDatagram"; A stubborn object intended to do anything possible to avoid being utilized.
        """
        return FakeDatagram()
