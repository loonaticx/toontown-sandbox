import time

from panda3d.core import *
import os
import string

from direct.directnotify import DirectNotifyGlobal
from direct.gui import DirectGuiGlobals
from direct.gui.DirectLabel import DirectLabel
from otp.otpbase.OTPBase import OTPBase
from otp.otpbase import OTPGlobals
from toontown.toonbase import ToontownGlobals, ToontownLoader, ToonBase, ToontownAccess, ToontownSettings
from toontown.toonbase import TTLocalizer


class ModularBase(ToonBase.ToonBase):
    def __init__(self, pipe = 'pandagl', wantHotkeys=True):
        self.selectedPipe = pipe
        OTPBase.__init__(self)

        self.modular = True

        # TODO: CLEANUP LATER

        if not config.GetInt('ignore-user-options', 0):
            self.settings = ToontownSettings.ToontownSettings()
            self.loadFromSettings()
        else:
            self.settings = None

        if wantHotkeys:
            self.accept('c', self.toggleCollisions)
            self.accept('x', self.toggleRenderCollisions)
            self.accept('q', self.exitShow)
            self.accept('o', base.oobe)
            self.accept('shift-o', base.oobeCull)
            self.accept('a', base.toggleBounds)
            self.accept('s', base.toggleTightBounds)
            self.accept('b', base.toggleBackface)
            self.accept('shift-r', base.win.gsg.releaseAll)
            self.accept('1', self.toggleGui)
            self.accept('2', self.toggleGUIPopup)
            self.accept('3', self.toggleFrameRateMeter)
            self.accept('4', self.toggleSGMeter)
            self.accept('w', base.toggleWireframe)
            self.accept('e', base.renderModeWireframe)
            self.accept('v', self.toggleVertexPainting)
            self.accept('shift-v', base.toggleShowVertices)
            self.accept('t', base.toggleTexture)
            self.accept('shift-a', render.analyze)
            self.accept('shift-l', render.ls)
            self.accept('f1', base.toggleTexMem)


        self.vertexPaintingToggled = False
        self.renderWireframeEnabled = False
        self.tightboundsToggled = False
        self.boundsToggled = False
        self.SGMeterToggled = False
        self.collisionsToggled = False
        self.renderCollisions = False
        self.frameMeterEnabled = False

        self.localAvatar = None
        self.disableShowbaseMouse()
        self.addCullBins()
        base.debugRunningMultiplier /= OTPGlobals.ToonSpeedFactor
        self.toonChatSounds = self.config.GetBool('toon-chat-sounds', 1)
        self.placeBeforeObjects = config.GetBool('place-before-objects', 1)
        self.endlessQuietZone = False
        self.wantDynamicShadows = 0
        self.exitErrorCode = 0
        camera.setPosHpr(0, 0, 0, 0, 0, 0)
        self.camLens.setMinFov(ToontownGlobals.DefaultCameraFov / (4. / 3.))
        self.camLens.setNearFar(ToontownGlobals.DefaultCameraNear, ToontownGlobals.DefaultCameraFar)
        self.musicManager.setVolume(0.65)
        self.setBackgroundColor(ToontownGlobals.DefaultBackgroundColor)
        tpm = TextPropertiesManager.getGlobalPtr()
        candidateActive = TextProperties()
        candidateActive.setTextColor(0, 0, 1, 1)
        tpm.setProperties('candidate_active', candidateActive)
        candidateInactive = TextProperties()
        candidateInactive.setTextColor(0.3, 0.3, 0.7, 1)
        tpm.setProperties('candidate_inactive', candidateInactive)
        self.transitions.IrisModelName = 'phase_3/models/misc/iris'
        self.transitions.FadeModelName = 'phase_3/models/misc/fade'
        self.exitFunc = self.userExit
        if 'launcher' in __builtins__ and launcher:
            launcher.setPandaErrorCode(11)
        globalClock.setMaxDt(0.2)
        if self.config.GetBool('want-particles', 1) == 1:
            self.notify.debug('Enabling particles')
            self.enableParticles()
        self.accept(ToontownGlobals.ScreenshotHotkey, self.takeScreenShot)
        self.accept('panda3d-render-error', self.panda3dRenderError)
        oldLoader = self.loader
        self.loader = ToontownLoader.ToontownLoader(self)
        __builtins__['loader'] = self.loader
        oldLoader.destroy()
        self.accept('PandaPaused', self.disableAllAudio)
        self.accept('PandaRestarted', self.enableAllAudio)
        self.friendMode = self.config.GetBool('switchboard-friends', 0)
        self.wantPets = self.config.GetBool('want-pets', 1)
        self.wantBingo = self.config.GetBool('want-fish-bingo', 1)
        self.wantKarts = self.config.GetBool('want-karts', 1)
        self.wantNewSpecies = self.config.GetBool('want-new-species', 0)
        self.inactivityTimeout = self.config.GetFloat('inactivity-timeout', ToontownGlobals.KeyboardTimeout)
        if self.inactivityTimeout:
            self.notify.debug('Enabling Panda timeout: %s' % self.inactivityTimeout)
            self.mouseWatcherNode.setInactivityTimeout(self.inactivityTimeout)
        self.randomMinigameAbort = self.config.GetBool('random-minigame-abort', 0)
        self.randomMinigameDisconnect = self.config.GetBool('random-minigame-disconnect', 0)
        self.randomMinigameNetworkPlugPull = self.config.GetBool('random-minigame-netplugpull', 0)
        self.autoPlayAgain = self.config.GetBool('auto-play-again', 0)
        self.skipMinigameReward = self.config.GetBool('skip-minigame-reward', 0)
        self.wantMinigameDifficulty = self.config.GetBool('want-minigame-difficulty', 0)
        self.minigameDifficulty = self.config.GetFloat('minigame-difficulty', -1.0)
        if self.minigameDifficulty == -1.0:
            del self.minigameDifficulty
        self.minigameSafezoneId = self.config.GetInt('minigame-safezone-id', -1)
        if self.minigameSafezoneId == -1:
            del self.minigameSafezoneId
        cogdoGameSafezoneId = self.config.GetInt('cogdo-game-safezone-id', -1)
        cogdoGameDifficulty = self.config.GetFloat('cogdo-game-difficulty', -1)
        if cogdoGameDifficulty != -1:
            self.cogdoGameDifficulty = cogdoGameDifficulty
        if cogdoGameSafezoneId != -1:
            self.cogdoGameSafezoneId = cogdoGameSafezoneId
        # ToontownBattleGlobals.SkipMovie = self.config.GetBool('skip-battle-movies', 0)
        self.creditCardUpFront = self.config.GetInt('credit-card-up-front', -1)
        if self.creditCardUpFront == -1:
            del self.creditCardUpFront
        else:
            self.creditCardUpFront = self.creditCardUpFront != 0
        self.housingEnabled = self.config.GetBool('want-housing', 1)
        self.cannonsEnabled = self.config.GetBool('estate-cannons', 0)
        self.fireworksEnabled = self.config.GetBool('estate-fireworks', 0)
        self.dayNightEnabled = self.config.GetBool('estate-day-night', 0)
        self.cloudPlatformsEnabled = self.config.GetBool('estate-clouds', 0)
        self.greySpacing = self.config.GetBool('allow-greyspacing', 0)
        self.goonsEnabled = self.config.GetBool('estate-goon', 0)
        self.restrictTrialers = self.config.GetBool('restrict-trialers', 1)
        self.roamingTrialers = self.config.GetBool('roaming-trialers', 1)
        self.slowQuietZone = self.config.GetBool('slow-quiet-zone', 0)
        self.slowQuietZoneDelay = self.config.GetFloat('slow-quiet-zone-delay', 5)
        self.killInterestResponse = self.config.GetBool('kill-interest-response', 0)
        tpMgr = TextPropertiesManager.getGlobalPtr()
        WLDisplay = TextProperties()
        WLDisplay.setSlant(0.3)
        WLEnter = TextProperties()
        WLEnter.setTextColor(1.0, 0.0, 0.0, 1)
        tpMgr.setProperties('WLDisplay', WLDisplay)
        tpMgr.setProperties('WLEnter', WLEnter)
        del tpMgr
        self.lastScreenShotTime = globalClock.getRealTime()
        # self.accept('InputState-forward', self.__walking)
        self.canScreenShot = 1
        self.glitchCount = 0
        self.walking = 0
        self.oldX = max(1, base.win.getXSize())
        self.oldY = max(1, base.win.getYSize())
        self.aspectRatio = float(self.oldX) / self.oldY

    def initCR(self, serverVersion = 'tto-dev'):
        """
        CR isn't initialized when HeadlessBase is initialized, courtesy to local modular instances that don't
        need to use any networking.
        """
        from toontown.distributed import ToontownClientRepository
        self.cr = ToontownClientRepository.ToontownClientRepository(serverVersion, launcher)

    def startConnection(self):
        """
        This requires a local server to be up and running.
        """
        if base.cr is None:
            self.notify.error("startHeadlessShow(): You forgot to call base.initCR() first!")
            return

        gameServer = '127.0.0.1'

        # Get the base port.
        serverPort = ConfigVariableInt('server-port', 7198).getValue()

        serverList = []
        for name in gameServer.split(';'):
            if name == "localhost":
                name = "127.0.0.1"
            url = URLSpec(name, 1)
            url.setScheme('https')
            if url.getServer() == "127.0.0.1":
                url.setScheme('http')

            if not url.hasPort():
                url.setPort(serverPort)
            serverList.append(url)

        # Connect to the server (This causes the screen to show the "Connecting..." screen.
        self.cr.loginFSM.request('connect', [serverList])

        self.ttAccess = ToontownAccess.ToontownAccess()
        self.ttAccess.initModuleInfo()

    def generateLocalAvatar(self):
        assert base.cr
        from toontown.toon.LocalToon import LocalToon
        lt = LocalToon(base.cr)
        base.localAvatar = lt
        from modular.distributed.FakeDCClass import FakeDCClass
        base.localAvatar.dclass = FakeDCClass()
        # base.localAvatar.dclass = base.cr.dclassesByName['DistributedToon']

        from toontown.toon.ToonDNA import ToonDNA
        dna = ToonDNA()
        base.localAvatar.dna = dna
        dna.newToonRandom()
        base.localAvatar.doId = 1
        base.localAvatar.setDNA(dna)
        base.localAvatar.reparentTo(render)
        base.localAvatar.useWalkControls()
        base.localAvatar.enableAvatarControls()
        base.localAvatar.attachCamera()
        base.localAvatar.enableRun()
        base.localAvatar.defaultShard = 0
        # Create a convenient global
        __builtins__['localAvatar'] = base.localAvatar

        base.localAvatar.generate()

    def initMarginManager(self):
        self.marginManager = MarginManager()
        self.margins = self.aspect2d.attachNewNode(self.marginManager, DirectGuiGlobals.MIDGROUND_SORT_INDEX + 1)
        mm = self.marginManager
        self.leftCells = [mm.addGridCell(0, 1, -1.33333333333, 1.33333333333, -1.0, 1.0, base.a2dTopLeft, (0.222222, 0, -1.5)), mm.addGridCell(0, 2, -1.33333333333, 1.33333333333, -1.0, 1.0, base.a2dTopLeft, (0.222222, 0, -1.16667)), mm.addGridCell(0, 3, -1.33333333333, 1.33333333333, -1.0, 1.0, base.a2dTopLeft, (0.222222, 0, -0.833333))]
        self.bottomCells = [mm.addGridCell(0.5, 0, -1.33333333333, 1.33333333333, -1.0, 1.0, base.a2dBottomCenter, (-0.888889, 0, 0.166667)),
         mm.addGridCell(1.5, 0, -1.33333333333, 1.33333333333, -1.0, 1.0, base.a2dBottomCenter, (-0.444444, 0, 0.166667)),
         mm.addGridCell(2.5, 0, -1.33333333333, 1.33333333333, -1.0, 1.0, base.a2dBottomCenter, (0, 0, 0.166667)),
         mm.addGridCell(3.5, 0, -1.33333333333, 1.33333333333, -1.0, 1.0, base.a2dBottomCenter, (0.444444, 0, 0.166667)),
         mm.addGridCell(4.5, 0, -1.33333333333, 1.33333333333, -1.0, 1.0, base.a2dBottomCenter, (0.888889, 0, 0.166667))]
        self.rightCells = [mm.addGridCell(5, 2, -1.33333333333, 1.33333333333, -1.0, 1.0, base.a2dTopRight, (-0.222222, 0, -1.16667)), mm.addGridCell(5, 1, -1.33333333333, 1.33333333333, -1.0, 1.0, base.a2dTopRight, (-0.222222, 0, -1.5))]



    def toggleCollisions(self):
        base.collisionsToggled = not base.collisionsToggled
        if not base.collisionsToggled:
            """
            Toggles the display of collision bounds surrounding the invoker.
            """
            base.cTrav.showCollisions(render)
            base.shadowTrav.showCollisions(render)
        else:
            base.cTrav.hideCollisions()
            base.shadowTrav.hideCollisions()

    def toggleRenderCollisions(self):
        """
        Displays collision bounds for currently rendered objects.
        """
        print("toggleRenderCollisions")
        base.renderCollisions = not base.renderCollisions
        if not base.renderCollisions:
            render.findAllMatches('**/+CollisionNode').show()
        else:
            render.findAllMatches('**/+CollisionNode').hide()

    def toggleGUIPopup(self):
        """
        Debug utility function
        """
        if self.cr.guiPopupShown:
            self.mouseWatcherNode.hideRegions()
            self.cr.guiPopupShown = 0
        else:
            self.mouseWatcherNode.showRegions(render2d, 'gui-popup', 0)
            self.cr.guiPopupShown = 1

    def toggleOSD(self):
        """
        Toggle On Screen Debug functionality
        """
        if not base.osd:
            self.notify.info("Enabling OSD...")
            onScreenDebug.enabled = True
            base.osd = True
            self.notify.info("OSD is enabled.")
        else:
            self.notify.info("Disabling OSD...")
            onScreenDebug.enabled = False
            base.osd = False
            self.notify.info("OSD has been disabled.")
        return base.osd

    def toggleVertexPainting(self):
        if not base.vertexPaintingToggled:
            render.setColor(1, 1, 1)
            base.vertexPaintingToggled = True
        else:
            render.clearColor()
            base.vertexPaintingToggled = False

    def toggleTightBounds(self):
        if not base.tightboundsToggled or base.boundsToggled:
            for node in render.findAllMatches("**/*"):
                node.showTightBounds()
            base.tightboundsToggled = True
            base.boundsToggled = False
        else:
            for node in render.findAllMatches("**/*"):
                node.hideBounds()
            base.tightboundsToggled = base.boundsToggled = False

    def toggleBounds(self):
        if not base.boundsToggled or base.tightboundsToggled:
            for node in render.findAllMatches("**/*"):
                node.showBounds()
            base.boundsToggled = True
            base.tightboundsToggled = False
        else:
            for node in render.findAllMatches("**/*"):
                node.hideBounds()
            base.boundsToggled = base.tightboundsTarget = False

    def renderModeWireframe(self, red = 255, green = 0, blue = 0, alpha = 255, thickness = 1.0):
        r = red / 255
        g = green / 255
        b = blue / 255
        a = alpha / 255
        if not base.renderWireframeEnabled:
            for node in render.findAllMatches("**/*"):
                node.setRenderModeFilledWireframe(LColor(r, g, b, a))
                node.setRenderModeThickness(thickness)
            base.renderWireframeEnabled = True
            return "Rendered the scene with a wireframe overlay."
        else:
            for node in render.findAllMatches("**/*"):
                node.setRenderModeFilled()
            base.renderWireframeEnabled = False
            return "Cleared wireframe."

    def toggleSGMeter(self):
        base.SGMeterToggled = not base.SGMeterToggled
        base.setSceneGraphAnalyzerMeter(base.SGMeterToggled)

    def toggleFrameRateMeter(self):
        base.frameMeterEnabled = not base.frameMeterEnabled
        base.setFrameRateMeter(base.frameMeterEnabled)

    def enableSoftwareMousePointer(self):
        """
        Creates some geometry and parents it to render2d to show
        the currently-known mouse position.  Useful if the mouse
        pointer is invisible for some reason.
        """
        # this is here because showbase wants to load in the STUPID model in the root of the directory
        mouseViz = self.render2d.attachNewNode('mouseViz')
        lilsmiley = self.loader.loadModel('models/misc/lilsmiley')
        lilsmiley.reparentTo(mouseViz)

        aspectRatio = self.getAspectRatio()
        # Scale the smiley face to 32x32 pixels.
        height = self.win.getSbsLeftYSize()
        lilsmiley.setScale(
            32.0 / height / aspectRatio,
            1.0, 32.0 / height)
        self.mouseWatcherNode.setGeometry(mouseViz.node())


    def toggleGui(self):
        if not self.guiToggleDisabled:
            if aspect2d.isHidden():
                aspect2d.show()
            else:
                aspect2d.hide()

    def resetGSG(self):
        base.win.gsg.releaseAll()
