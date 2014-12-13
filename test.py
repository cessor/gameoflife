
from OpenGL.GL import *
from OpenGL.GLU import *
import os
import pygame
import random
from pygame.locals import *

# creatureSize = 10
# width,height = environmentWidth,environmentHeight = 100,100
# screenSize = width * creatureSize, height * creatureSize

from collections import namedtuple

NUM_CELLS = 100
Resolution = namedtuple('Resolution', ['x','y'])
RESOLUTION = Resolution(1280, 800)

limit = min(RESOLUTION)
pixel_per_cell = limit / float(NUM_CELLS)

# 1920, 1080 # wide a 
# 1920, 1200 # wide b
# 1440, 900 # wide
# 1280, 800 # rect
# 1024, 768 # rect


def makeMatrix(width, height, fn):
    matrix = []
    for x in range(width):
        matrix.append([])
        for y in range(height):
            matrix[x].append(fn(x,y))
    return matrix

class Color(object):
    red = (1.0, 0.0, 0.0, 1.0)
    green = (0.0, 0.86, 0.0, 1.0)
    anthracite = (0.15, 0.15, 0.13, 1.0)
    black = (0.0, 0.0, 0.0, 1.0)
    white = (1.0, 1.0, 1.0, 1.0)

dead = 0
alive = 1

def empty(x,y):
    return dead

def randomCell(x,y):
    return random.randint(dead, alive)


class Cell(object):
    def __init__(self,x,y,value):
        self.x = x
        self.y = y
        self.value = value

    def isAlive(self):
        return self.value == alive

class Environment(object):
    def __init__(self):
        self.clear()

    def randomize(self):
        self.environment = makeMatrix(NUM_CELLS, NUM_CELLS, randomCell)

    def clear(self):
        self.environment = makeMatrix(NUM_CELLS, NUM_CELLS, empty)

    def kill(self, x, y):
        self.environment[x][y] = dead

    def vitalize(self, x, y):
        self.environment[x][y] = alive

    def iterateField(self, field):
        width = len(field[0])
        height = len(field)
        return self.iterate(width, height, field)

    def iterate(self, width, height, field):
        for x in range(width):
            for y in range(height): 
                yield (x,y,field[x][y])

    def cells(self):
        return self.iterateField(self.environment)

    def getNeighborCount(self, x,y):
        count = 0
        xpn = (x + 1) % NUM_CELLS
        ypn = (y + 1) % NUM_CELLS

        count += self.isAlive(x, ypn)
        count += self.isAlive(xpn, ypn)
        count += self.isAlive(xpn, y)
        count += self.isAlive(xpn, y - 1)
        count += self.isAlive(x, y - 1)
        count += self.isAlive(x - 1, y - 1)
        count += self.isAlive(x - 1, y)
        count += self.isAlive(x - 1, ypn)
        return count

    def isAlive(self,x,y):
        return (self.environment[x][y] == alive)

    def decide(self,x,y,neighbors):
        if 2 <= neighbors <= 3:
            if neighbors == 3:
                self.vitalize(x,y)
            else:
                pass
        else: 
            self.kill(x,y)

    def calculateNextGeneration(self):
        neighborhood = makeMatrix(NUM_CELLS, NUM_CELLS, self.getNeighborCount)
        for x,y,neighbors in self.iterateField(neighborhood):
            self.decide(x, y, neighbors)

def draw_grid():
    glColor4f(*Color.anthracite)
    boundary = NUM_CELLS * pixel_per_cell
    glRectf(0,0, boundary, boundary)
    glLineWidth(1)
    glColor4f(*Color.black)
    glBegin(GL_LINES);
    for i in xrange(0, int(boundary), int(pixel_per_cell)):
        glVertex2f(i, 0)
        glVertex2f(i, boundary)
        glVertex2f(0, i)
        glVertex2f(boundary, i)
    glEnd()

def draw_cells(environment):
    for x,y,v in environment.cells():
        if environment.isAlive(x,y):
            drawCell(x,y, pixel_per_cell, Color.green)

def draw(environment):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslate(0.0, 0.0, 3.0)

    draw_grid()
    draw_cells(environment)
      

def drawCell(x,y,size,color):
    x = x * size
    y = y * size
    glColor4f(*color)
    glRectf(x,y, (size - 1) + x, (size - 1) + y)
    #glVertex3f(x, y, 0.0)
    #glVertex3f((size - 1) + x, y, 0.0)
    #glVertex3f((size - 1) + x, (size - 1) + y, 0.0)
    #glVertex3f(x, (size - 1) + y, 0.0)

def setupGraphics():
    pygame.init()
    global font
    global surface
    font = pygame.font.Font(None, 28)
    os.environ['SDL_VIDEO_WINDOW_POS'] = '%i,%i' % (0, 0)
    video_flags = OPENGL | DOUBLEBUF | NOFRAME  | FULLSCREEN
    surface = pygame.display.set_mode(RESOLUTION, video_flags)
    glClearColor(*Color.black)
    resize(RESOLUTION)

def resize((width, height)):
    glViewport(0,0, width,height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, width, height, 0, -20, 0.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
def isexit(event):
    return event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE)

def ispaused(event):
    return event.type == KEYDOWN and event.key == K_p

def markedCell():
    x,y = pygame.mouse.get_pos()
    cell = int(x / pixel_per_cell), int(y / pixel_per_cell)
    return cell

def snap_to_grid(x, y):
    x = int(x / pixel_per_cell)
    y = int(y / pixel_per_cell)
    return x,y

def draw_cursor():
    glColor4f(*Color.white)
    x,y = pygame.mouse.get_pos()
    x,y = snap_to_grid(x, y)
    glColor4f(*Color.red)
    x = (x * pixel_per_cell)
    y = (y * pixel_per_cell)
    glRectf(x, y, x + pixel_per_cell, y+pixel_per_cell)

def handleEvents(event, environment):
    if event.type == MOUSEBUTTONDOWN:
        lmb,mmb,rmb = pygame.mouse.get_pressed()
        if lmb:
            environment.vitalize(*markedCell())
        if rmb:
            environment.kill(*markedCell())
    if event.type == KEYDOWN and event.key == K_F5:
        environment.randomize()
    if event.type == KEYDOWN and event.key == K_c:
        environment.clear()

caption = 'Game of Life - Generation %s'

def updateTitle(generations):
    pygame.display.set_caption(caption % generations)

def gameLoop(environment):
    paused = True

    generations = 0
    while True:
        updateTitle(generations)
        event = pygame.event.poll() 
        if isexit(event):
            break       

        if ispaused(event):
            paused = (not paused)

        handleEvents(event,environment)
        draw(environment)
        draw_cursor()

        if not paused:
            environment.calculateNextGeneration()
            generations += 1
        pygame.display.flip()

def main():
    environment = Environment()
    setupGraphics()

    frames = 0
    ticks = pygame.time.get_ticks()
    gameLoop(environment)

if __name__ == '__main__': 
    main()

