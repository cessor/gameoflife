from OpenGL.GL import *
from OpenGL.GLU import *
import os
import pygame
import random
import pygame.locals as pygame_locals
from pygame.locals import *


from config import *
from userinput import Events

def makeMatrix(width, height, fn):
    matrix = []
    for x in xrange(width):
        matrix.append([])
        for y in xrange(height):
            matrix[x].append(fn(x,y))
    return matrix

DEAD = 0
ALIVE = 1

def empty(x,y):
    return DEAD

def randomCell(x,y):
    return random.randint(DEAD, ALIVE)

class Environment(object):
    def __init__(self):
        self.live_cells = []
        self.clear()

    def randomize(self):
        self.environment = makeMatrix(NUM_CELLS, NUM_CELLS, randomCell)

    def clear(self):
        self.environment = makeMatrix(NUM_CELLS, NUM_CELLS, empty)

    def kill(self, x, y):
        self.environment[x][y] = DEAD

    def vitalize(self, x, y):
        self.environment[x][y] = ALIVE

    def iterate(self, width, height, field):
        for x in xrange(width):
            for y in xrange(height): 
                yield (x,y,field[x][y])

    def cells(self):
        return self.iterate(NUM_CELLS, NUM_CELLS, self.environment)

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
        return (self.environment[x][y] == ALIVE)

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
        for x,y,neighbors in self.iterate(NUM_CELLS, NUM_CELLS, neighborhood):
            self.decide(x, y, neighbors)

class Engine(object):
    def __init__(self):
        self.__setup()

    def __setup(self):
        pygame.init()
        os.environ['SDL_VIDEO_WINDOW_POS'] = '%i,%i' % (100, 100)
        video_flags = OPENGL | DOUBLEBUF
        if SHOW_FULLSCREEN:
            video_flags = video_flags | FULLSCREEN

        pygame.display.set_mode(RESOLUTION, video_flags)
        glClearColor(*BACKGROUND_COLOR)
        self.__resize(*RESOLUTION)

    def __resize(self, width, height):
        glViewport(0,0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0.0, width, height, 0, -20, 0.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()        

    def clear_screen(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslate(0.0, 0.0, 3.0)

    def draw_cell(self, x, y, size, color):
        x = x * size + OFFSET_X
        y = y * size + OFFSET_Y
        glColor4f(*color)
        glRectf(x,y, (size - 1) + x, (size - 1) + y)

    def frame(self):
        pygame.display.flip()

class Grid(object):
    def __init__(self, engine, environment):
        self._environment = environment
        self._engine = engine

    def draw(self):
        self._engine.clear_screen()
        self.__draw_grid()
        self.__draw_cells()
        self.__draw_cursor()

    def __draw_grid(self):
        glColor4f(*GRID_BACKDROP_COLOR)
        boundary_x = NUM_CELLS * PIXEL_PER_CELL + OFFSET_X
        boundary_y = NUM_CELLS * PIXEL_PER_CELL + OFFSET_Y
        glRectf(OFFSET_X, OFFSET_Y, boundary_x, boundary_y)
        if not SHOW_GRID: return

        glLineWidth(1)
        glColor4f(*GRID_LINE_COLOR)
        glBegin(GL_LINES);
        for i in xrange(PIXEL_PER_CELL, NUM_CELLS * PIXEL_PER_CELL, PIXEL_PER_CELL):
            glVertex2f(i + OFFSET_X, OFFSET_Y)
            glVertex2f(i + OFFSET_X, boundary_y)
            glVertex2f(OFFSET_X,   i + OFFSET_Y)
            glVertex2f(boundary_x, i + OFFSET_Y)
        glEnd()

    def __draw_cells(self):
        for x,y,v in self._environment.cells():
            if self._environment.isAlive(x,y):
                self._engine.draw_cell(x,y, PIXEL_PER_CELL, CELL_COLOR)
          
    def __draw_cursor(self):
        position = pygame.mouse.get_pos()
        x,y = self.__pixel_to_grid(position)
        self._engine.draw_cell(x, y, PIXEL_PER_CELL, CURSOR_COLOR)
        
    def __pixel_to_grid(self, (x, y)):
        x,y = self.__snap_to_grid(x - OFFSET_X, y - OFFSET_Y)
        return x,y

    def __snap_to_grid(self, x, y):
        x = int(x / PIXEL_PER_CELL)
        y = int(y / PIXEL_PER_CELL)
        return x,y

    def __is_on_grid(self, x, y):
        return 0 <= x < NUM_CELLS and 0 <= y < NUM_CELLS

    def vitalize_cell(self, position):
        x,y = self.__pixel_to_grid(position)
        if not self.__is_on_grid(x,y): return
        self._environment.vitalize(x,y)

    def kill_cell(self, position):
        x,y = self.__pixel_to_grid(position)
        if not self.__is_on_grid(x,y): return
        self._environment.kill(x,y)

class Game(object):
    def __init__(self, engine, grid, environment, events=Events()):
        self._engine = engine
        self._events = events
        self._grid = grid
        self._environment = environment

        self._running = True
        self._paused = True
        self.__register_events()

    def __register_events(self):
        self._events.on_quit(self.quit)

        keyboard = self._events._keyboard
        keyboard.on_key(K_ESCAPE, self.quit)
        keyboard.on_key(K_q, self.quit)
        keyboard.on_key(K_p, self.pause)
        keyboard.on_key(K_F5, self._environment.randomize)
        keyboard.on_key(K_c, self._environment.clear)

        mouse = self._events._mouse
        mouse.on_click(self._grid.vitalize_cell)
        mouse.on_right_click(self._grid.kill_cell)

    def run(self):
        ## Put this here for game syncing stuff 
        # frames = 0
        # ticks = pygame.time.get_ticks()
        while self._running:
            self._events.handle()
            self._grid.draw()
            if not self._paused:
                self.round()
            self._engine.frame()

    def round(self):
        self._environment.calculateNextGeneration()

    def pause(self):
        self._paused = (not self._paused)
        
    def quit(self):
        self._running = False

def main():
    engine = Engine()
    environment = Environment()
    grid = Grid(engine, environment)
    Game(engine, grid, environment).run()

if __name__ == '__main__': 
    main()