from modular.toontown.toonbase import ModularStart
from modular.toontown.toonbase.ModularBase import ModularBase

base = ModularBase()
base.initCR()

base.generateLocalAvatar()
testModel = loader.loadModel("phase_4/models/neighborhoods/toontown_central")
testModel.reparentTo(render)

# base.modular = False
base.startConnection()

base.oobe()
base.run()
