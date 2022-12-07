from direct.fsm import State


from modular.toontown.toonbase import ModularStart
from modular.toontown.toonbase.ModularBase import ModularBase

base = ModularBase()
base.initCR()
base.generateLocalAvatar()

from toontown.coghq.DistributedFactory import DistributedFactory

dfact = DistributedFactory(base.cr)
dfact.doId = 2
dfact.generate()
dfact.factoryId = 11500
dfact.zoneIds = []
for i in range(1, 999):
    dfact.zoneIds.append(i)
# dfact.zoneIds = [1, 2, 3, 4, 5]
dfact.startTime = 0
dfact.entranceId = 0
dfact.avIdList = [base.localAvatar.doId]
dfact.levelZone = 1
base.localAvatar.defaultShard = 0
dfact.dclass = base.cr.dclassesByName['DistributedFactory']
dfact.levelAnnounceGenerate()
from toontown.coghq.SellbotLegFactorySpec import *
from otp.level import LevelSpec
factSpec = LevelSpec.LevelSpec(levelSpec)
dfact.privGotSpec(factSpec)
dfact.placeLocalToon()

entityCreator = dfact.createEntityCreator()

for zone in dfact.zoneIds:
    dfact.showZone(zone)

base.localAvatar.reparentTo(render.find("**/LegFactory"))
# base.localAvatar.setPos( 20.7079, 26.1823, 3.72601)


base.oobe()

base.run()