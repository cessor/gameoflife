import pygame 
from pygame.locals import KEYDOWN, MOUSEBUTTONDOWN, QUIT

class InputDevice(object):
    def handle(self, event):
        pass

class Mouse(InputDevice):
    def __init__(self):
        self.__click = lambda p:None
        self.__right_click = lambda p:None

    def __mouse_clicked(self, event):
        return event.type == MOUSEBUTTONDOWN

    def on_click(self, fn):
        self.__click = fn

    def on_right_click(self, fn):
        self.__right_click = fn

    def handle(self, event):
        if self.__mouse_clicked(event):
            lmb,mmb,rmb = pygame.mouse.get_pressed()
            position = pygame.mouse.get_pos()
            if lmb: self.__click(position)
            if rmb: self.__right_click(position)

class Keyboard(InputDevice):
    def __init__(self):
        self.__keymap = {}

    def __key_down(self, event):
        return event.type == KEYDOWN

    def on_key(self, key, fn):
        self.__keymap[key] = fn

    def handle(self, event):
        if not self.__key_down(event): 
            return
        self.__keymap.get(event.key, lambda:None)()

class Events(object):
    def __init__(self, keyboard=Keyboard(), mouse=Mouse()):
        self.__quit = lambda:None
        self._keyboard = keyboard
        self._mouse = mouse

    def handle(self):
        event = pygame.event.poll()
        # Window Quit
        if event.type == QUIT:
            self.__quit()
        self._keyboard.handle(event)
        self._mouse.handle(event)

    def on_quit(self, fn):
        'Handles Window Quit Event'
        self.__quit = fn