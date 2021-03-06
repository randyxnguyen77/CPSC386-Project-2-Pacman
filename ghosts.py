import pygame
from entity import MazeRunner
from constants import *
from vector import Vector
from random import randint
from modes import Mode
from stack import Stack
from animation import Animation


class Ghost(MazeRunner):
    def __init__(self, nodes, spritesheet):
        MazeRunner.__init__(self, nodes, spritesheet)
        self.name = "ghost"
        self.goal = Vector()
        self.modeStack = self.setupModeStack()
        self.mode = self.modeStack.pop()
        self.modeTimer = 0
        self.spawnNode = self.findSpawnNode()
        self.setGuideStack()
        self.pelletsForRelease = 0
        self.released = True
        self.bannedDirections = []
        self.setStartPosition()
        self.points = 200
        self.animation = None
        self.animations = {}

    def findStartNode(self):
        for node in self.nodes.homeList:
            if node.homeEntrance:
                return node
        return node

    def setStartPosition(self):
        self.node = self.findStartNode()
        self.target = self.node
        self.setPosition()

    def getClosestDirection(self, validDirections):
        distances = []
        for direction in validDirections:
            diffVec = self.node.position + direction * TILEWIDTH - self.goal
            distances.append(diffVec.magnitudeSquared())
        index = distances.index(min(distances))
        return validDirections[index]

    def getValidDirections(self):
        validDirections = []
        for key in self.node.neighbors.keys():
            if self.node.neighbors[key] is not None:
                if key != self.direction * -1:
                    if not self.mode.name == "SPAWN":
                        if not self.node.homeEntrance:
                            if key not in self.bannedDirections:
                                validDirections.append(key)
                        else:
                            if key != DOWN:
                                validDirections.append(key)
                    else:
                        validDirections.append(key)
        if len(validDirections) == 0:
            validDirections.append(self.forceBacktrack())

        return validDirections

    def randomDirection(self, validDirections):
        index = randint(0, len(validDirections) - 1)
        return validDirections[index]

    def moveBySelf(self):
        if self.overshotTarget():
            # if self.name == "inky" and self.mode.name == "SPAWN": print("OVERSHOT NODE")
            self.node = self.target
            self.portal()
            validDirections = self.getValidDirections()
            self.direction = self.getClosestDirection(validDirections)

            self.target = self.node.neighbors[self.direction]
            # if self.name == "inky" and self.mode.name == "SPAWN":
            #    print("Direction = " + str(self.direction))
            #    print("Target Node = " + str(self.target.position))
            #    print("")
            self.setPosition()

            if self.mode.name == "SPAWN":
                if self.position == self.goal:  # reached the spawn goal
                    self.mode = self.modeStack.pop()  # should be the first GUIDE mode
                    self.direction = self.mode.direction
                    self.target = self.node.neighbors[self.direction]
                    self.setPosition()
            elif self.mode.name == "GUIDE":
                self.mode = self.modeStack.pop()
                if self.mode.name == "GUIDE":  # We're still guiding
                    self.direction = self.mode.direction
                    self.target = self.node.neighbors[self.direction]
                    self.setPosition()

    def reverseDirection(self):
        if self.mode.name != "GUIDE" and self.mode.name != "SPAWN":
            MazeRunner.reverseDirection(self)

    def setupModeStack(self):
        modes = Stack()
        modes.push(Mode(name="CHASE"))
        modes.push(Mode(name="SCATTER", time=5))
        modes.push(Mode(name="CHASE", time=20))
        modes.push(Mode(name="SCATTER", time=7))
        modes.push(Mode(name="CHASE", time=20))
        modes.push(Mode(name="SCATTER", time=7))
        modes.push(Mode(name="CHASE", time=20))
        modes.push(Mode(name="SCATTER", time=7))
        return modes

    def scatterGoal(self):
        self.goal = Vector(SCREENSIZE[0], 0)

    def chaseGoal(self, pacman, blinky=None):
        self.goal = pacman.position

    def modeUpdate(self, dt):
        self.modeTimer += dt
        if self.mode.time is not None:
            if self.modeTimer >= self.mode.time:
                self.reverseDirection()
                self.mode = self.modeStack.pop()
                self.modeTimer = 0

    def update(self, dt, pacman, blinky):
        self.visible = True
        self.portalSlowdown()
        speedMod = self.speed * self.mode.speedMult
        self.position += self.direction * speedMod * dt
        self.modeUpdate(dt)
        if self.mode.name == "CHASE":
            self.chaseGoal(pacman, blinky)
        elif self.mode.name == "SCATTER":
            self.scatterGoal()
        elif self.mode.name == "FREIGHT":
            self.randomGoal()
        elif self.mode.name == "SPAWN":
            self.spawnGoal()
        self.moveBySelf()
        self.updateAnimation(dt)

    def portalSlowdown(self):
        self.speed = 100
        if self.node.portalNode or self.target.portalNode:
            self.speed = 50

    def freightMode(self):
        if self.mode.name != "SPAWN" and self.mode.name != "GUIDE":
            if self.mode.name != "FREIGHT":
                if self.mode.time is not None:
                    dt = self.mode.time - self.modeTimer
                    self.modeStack.push(Mode(name=self.mode.name, time=dt))
                else:
                    self.modeStack.push(Mode(name=self.mode.name))
                self.mode = Mode("FREIGHT", time=7, speedMult=0.5)
                self.modeTimer = 0
            else:
                self.mode = Mode("FREIGHT", time=7, speedMult=0.5)
                self.modeTimer = 0
            self.reverseDirection()

    def randomGoal(self):
        x = randint(0, NCOLS * TILEWIDTH)
        y = randint(0, NROWS * TILEHEIGHT)
        self.goal = Vector(x, y)

    def spawnMode(self, speed=1):
        self.mode = Mode("SPAWN", speedMult=speed)
        self.modeTimer = 0
        for d in self.guide:
            self.modeStack.push(Mode("GUIDE", speedMult=0.5, direction=d))

    def findSpawnNode(self):
        for node in self.nodes.homeList:
            if node.spawnNode:
                break
        return node

    def spawnGoal(self):
        self.goal = self.spawnNode.position

    def setGuideStack(self):
        self.guide = [UP]

    def forceBacktrack(self):
        if self.direction * -1 == UP:
            return UP
        if self.direction * -1 == DOWN:
            return DOWN
        if self.direction * -1 == LEFT:
            return LEFT
        if self.direction * -1 == RIGHT:
            return RIGHT

    def defineAnimations(self, row):
        anim = Animation("loop")
        anim.speed = 10
        anim.addFrame(self.spritesheet.getImage(0, row, TILEWIDTH * 2, TILEHEIGHT * 2))
        anim.addFrame(self.spritesheet.getImage(1, row, TILEWIDTH * 2, TILEHEIGHT * 2))
        self.animations["up"] = anim

        anim = Animation("loop")
        anim.speed = 10
        anim.addFrame(self.spritesheet.getImage(2, row, TILEWIDTH * 2, TILEHEIGHT * 2))
        anim.addFrame(self.spritesheet.getImage(3, row, TILEWIDTH * 2, TILEHEIGHT * 2))
        self.animations["down"] = anim

        anim = Animation("loop")
        anim.speed = 10
        anim.addFrame(self.spritesheet.getImage(4, row, TILEWIDTH * 2, TILEHEIGHT * 2))
        anim.addFrame(self.spritesheet.getImage(5, row, TILEWIDTH * 2, TILEHEIGHT * 2))
        self.animations["left"] = anim

        anim = Animation("loop")
        anim.speed = 10
        anim.addFrame(self.spritesheet.getImage(6, row, TILEWIDTH * 2, TILEHEIGHT * 2))
        anim.addFrame(self.spritesheet.getImage(7, row, TILEWIDTH * 2, TILEHEIGHT * 2))
        self.animations["right"] = anim

        anim = Animation("loop")
        anim.speed = 10
        anim.addFrame(self.spritesheet.getImage(0, 6, TILEWIDTH * 2, TILEHEIGHT * 2))
        anim.addFrame(self.spritesheet.getImage(1, 6, TILEWIDTH * 2, TILEHEIGHT * 2))
        self.animations["freight"] = anim

        anim = Animation("loop")
        anim.speed = 10
        anim.addFrame(self.spritesheet.getImage(0, 6, TILEWIDTH * 2, TILEHEIGHT * 2))
        anim.addFrame(self.spritesheet.getImage(2, 6, TILEWIDTH * 2, TILEHEIGHT * 2))
        anim.addFrame(self.spritesheet.getImage(1, 6, TILEWIDTH * 2, TILEHEIGHT * 2))
        anim.addFrame(self.spritesheet.getImage(3, 6, TILEWIDTH * 2, TILEHEIGHT * 2))
        self.animations["flash"] = anim

        anim = Animation("static")
        anim.speed = 10
        anim.addFrame(self.spritesheet.getImage(4, 6, TILEWIDTH * 2, TILEHEIGHT * 2))
        self.animations["spawnup"] = anim

        anim = Animation("static")
        anim.speed = 10
        anim.addFrame(self.spritesheet.getImage(5, 6, TILEWIDTH * 2, TILEHEIGHT * 2))
        self.animations["spawndown"] = anim

        anim = Animation("static")
        anim.speed = 10
        anim.addFrame(self.spritesheet.getImage(6, 6, TILEWIDTH * 2, TILEHEIGHT * 2))
        self.animations["spawnleft"] = anim

        anim = Animation("static")
        anim.speed = 10
        anim.addFrame(self.spritesheet.getImage(7, 6, TILEWIDTH * 2, TILEHEIGHT * 2))
        self.animations["spawnright"] = anim

    def updateAnimation(self, dt):
        if self.mode.name == "SPAWN":
            if self.direction == UP:
                self.animation = self.animations["spawnup"]
            elif self.direction == DOWN:
                self.animation = self.animations["spawndown"]
            elif self.direction == LEFT:
                self.animation = self.animations["spawnleft"]
            elif self.direction == RIGHT:
                self.animation = self.animations["spawnright"]

        if self.mode.name in ["CHASE", "SCATTER"]:
            if self.direction == UP:
                self.animation = self.animations["up"]
            elif self.direction == DOWN:
                self.animation = self.animations["down"]
            elif self.direction == LEFT:
                self.animation = self.animations["left"]
            elif self.direction == RIGHT:
                self.animation = self.animations["right"]

        if self.mode.name == "FREIGHT":
            if self.modeTimer >= (self.mode.time * 0.7):
                self.animation = self.animations["flash"]
            else:
                self.animation = self.animations["freight"]
        self.image = self.animation.update(dt)


class Blinky(Ghost):
    def __init__(self, nodes, spritesheet):
        Ghost.__init__(self, nodes, spritesheet)
        self.name = "blinky"
        self.color = RED
        self.image = self.spritesheet.getImage(4, 2, TILEWIDTH * 2, TILEHEIGHT * 2)
        self.defineAnimations(2)
        self.animation = self.animations["left"]


class Pinky(Ghost):
    def __init__(self, nodes, spritesheet):
        Ghost.__init__(self, nodes, spritesheet)
        self.name = "pinky"
        self.color = PINK
        self.image = self.spritesheet.getImage(0, 3, TILEWIDTH * 2, TILEHEIGHT * 2)
        self.defineAnimations(3)
        self.animation = self.animations["up"]

    def scatterGoal(self):
        self.goal = Vector()

    def chaseGoal(self, pacman, blinky=None):
        self.goal = pacman.position + pacman.direction * TILEWIDTH * 4

    def setStartPosition(self):
        startNode = self.findStartNode()
        self.node = startNode.neighbors[DOWN]
        self.target = self.node
        self.setPosition()


class Inky(Ghost):
    def __init__(self, nodes, spritesheet):
        Ghost.__init__(self, nodes, spritesheet)
        self.name = "inky"
        self.color = TEAL
        self.pelletsForRelease = 30
        self.released = False
        self.image = self.spritesheet.getImage(2, 4, TILEWIDTH * 2, TILEHEIGHT * 2)
        self.defineAnimations(4)
        self.animation = self.animations["down"]

    def scatterGoal(self):
        self.goal = Vector(TILEWIDTH * NCOLS, TILEHEIGHT * NROWS)

    def chaseGoal(self, pacman, blinky=None):
        vec1 = pacman.position + pacman.direction * TILEWIDTH * 2
        vec2 = (vec1 - blinky.position) * 2
        self.goal = blinky.position + vec2

    def setStartPosition(self):
        self.bannedDirections = [RIGHT]
        startNode = self.findStartNode()
        pinkyNode = startNode.neighbors[DOWN]
        self.node = pinkyNode.neighbors[LEFT]
        self.target = self.node
        self.spawnNode = pinkyNode.neighbors[LEFT]
        self.setPosition()

    def setGuideStack(self):
        self.guide = [UP, RIGHT]


class Clyde(Ghost):
    def __init__(self, nodes, spritesheet):
        Ghost.__init__(self, nodes, spritesheet)
        self.name = "clyde"
        self.color = ORANGE
        self.pelletsForRelease = 60
        self.released = False
        self.image = self.spritesheet.getImage(2, 5, TILEWIDTH * 2, TILEHEIGHT * 2)
        self.defineAnimations(5)
        self.animation = self.animations["down"]

    def scatterGoal(self):
        self.goal = Vector(0, TILEHEIGHT * NROWS)

    def chaseGoal(self, pacman, blinky=None):
        d = pacman.position - self.position
        ds = d.magnitudeSquared()
        if ds <= (TILEWIDTH * 8) ** 2:
            self.scatterGoal()
        else:
            self.goal = pacman.position + pacman.direction * TILEWIDTH * 4

    def setStartPosition(self):
        self.bannedDirections = [LEFT]
        startNode = self.findStartNode()
        pinkyNode = startNode.neighbors[DOWN]
        self.node = pinkyNode.neighbors[RIGHT]
        self.spawnNode = pinkyNode.neighbors[RIGHT]
        self.target = self.node
        self.setPosition()

    def setGuideStack(self):
        self.guide = [UP, LEFT]


class GhostGroup(object):
    def __init__(self, nodes, spritesheet):
        self.nodes = nodes
        self.ghosts = [Blinky(nodes, spritesheet),
                       Pinky(nodes, spritesheet),
                       Inky(nodes, spritesheet),
                       Clyde(nodes, spritesheet)]

    def __iter__(self):
        return iter(self.ghosts)

    def update(self, dt, pacman):
        for ghost in self:
            ghost.update(dt, pacman, self.ghosts[0])

    def freightMode(self):
        for ghost in self:
            ghost.freightMode()

    def release(self, numPelletsEaten):
        for ghost in self:
            if not ghost.released:
                if numPelletsEaten >= ghost.pelletsForRelease:
                    ghost.bannedDirections = []
                    ghost.spawnMode()
                    ghost.released = True

    def updatePoints(self):
        for ghost in self:
            ghost.points *= 2

    def resetPoints(self):
        for ghost in self:
            ghost.points = 200

    def hide(self):
        for ghost in self:
            ghost.visible = False

    def render(self, screen):
        for ghost in self:
            ghost.render(screen)

