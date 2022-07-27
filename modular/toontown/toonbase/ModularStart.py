import sys
import time
import os
import random
import __builtin__

from panda3d.core import *

loadPrcFile('config/general.prc')
loadPrcFile('config/dev.prc')

# The VirtualFileSystem, which has already initialized, doesn't see the mount
# directives in the config(s) yet. We have to force it to load those manually:
vfs = VirtualFileSystem.getGlobalPtr()
mounts = ConfigVariableList('vfs-mount')
for mount in mounts:
    mountFile, mountPoint = (mount.split(' ', 2) + [None, None, None])[:2]
    vfs.mount(Filename(mountFile), Filename(mountPoint), 0)


class game:
    name = 'toontown'
    process = 'client'


__builtin__.game = game()

loadPrcFileData("", "model-path resources")
loadPrcFileData("", "default-model-extension .bam")

from direct.directnotify.DirectNotifyGlobal import directNotify

notify = directNotify.newCategory('ToontownStart')
notify.setInfo(True)

# This suppresses the "Unable to send datagram after connection is closed." warning
loadPrcFileData('', 'notify-level-distributed fatal')

try:
    launcher
except:
    from toontown.launcher.TTOffDummyLauncher import TTOffDummyLauncher

    launcher = TTOffDummyLauncher()
    __builtin__.launcher = launcher

from toontown.toonbase import ToontownGlobals

tempLoader = Loader()

from direct.gui import DirectGuiGlobals

DirectGuiGlobals.setDefaultFontFunc(ToontownGlobals.getInterfaceFont)
