from direct.fsm import State

from modular.toontown.toonbase import ModularStart
from modular.toontown.toonbase.ModularBase import ModularBase

base = ModularBase()
base.initCR()
base.generateLocalAvatar()

from toontown.coghq.FactoryUtil import CyclePlacer

InterestingLocations = [
    (
        # double staircase
        ((-866, -272, -40), -101),
        # stomper room
        ((-662, -242, 7.5), 0),
        # warehouse
        ((-20, -180, 20), 0),
        # left elevator
        ((-249, 258, 111), 0),
        # right elevator
        ((318, 241, 115), -16),
        # vista view of factory from left elevator
        ((-251, 241, 109), -180),
        # top of right silo
        ((296, 292, 703), 56),
        # platform jumping room
        ((-740, 122, 28), 90),
        # paint mixer room
        ((210, -270, 38), -90),
    ),
    (
        ((20, 21, 0), 0),
        ((3, 404, 39), -16),
        ((-496, 358, 5), 0),
    ),
]

factory = loader.loadModel("SellbotLegFactoryOld2")
factory.reparentTo(render)

CyclePlacer(InterestingLocations[0], 'f4-up')
base.camLens.setNearFar(1.0, 9999.0)

base.localAvatar.setCameraFov(90)
base.run()
