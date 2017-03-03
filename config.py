from collections import namedtuple

Resolution = namedtuple('Resolution', ['x', 'y'])
class Resolutions(object):
    resolutions = [
        (1920, 1200),
        (1920, 1080),
        (1680, 1050),
        (1440, 900),
        (1360, 768),
        (1280, 800),
        (1024, 640)
    ]

    @classmethod
    def parse(self, x, y):
        if (x,y) not in self.resolutions:
            resolutions = ', '.join(['%sx%s' % (a, b) for a,b in self.resolutions])
            raise Exception('Resolution %s x %s not supported. Available resolutions: %s' % (x,y, resolutions)  )
        return Resolution(x, y)

class Color(object):
    gray =        (0.15, 0.15,   0.13,   1.0)
    black =       (0.0, 0.0, 0.0, 1.0)
    white =       (1.0, 1.0, 1.0, 1.0)
    red =         (1.0, 0.2, 0.0, 1.0)
    orange =      (1.0, 0.4, 0.0, 1.0)
    yellow =      (1.0, 0.9, 0.0, 1.0)
    light_green = (0.4, 1.0, 0.0, 1.0)
    green =       (0.0, 1.0, 0.2, 1.0)
    cyan =        (0.0, 1.0, 0.4, 1.0)
    light_blue =  (0.0, 0.6, 1.0, 1.0)
    blue =        (0.0, 0.2, 1.0, 1.0)
    purple =      (0.4, 0.0, 1.0, 1.0)
    pink =        (1.0, 0.0, 0.8, 1.0)
    @classmethod
    def __colors(self):
        return [key for key in self.__dict__.keys() if not key.startswith('_') and key != 'named']
    @classmethod
    def named(self, name):
        if not hasattr(self, name):
            colors = ', '.join(self.__colors())
            raise Exception('Unknown color %s. Available colors are: %s' % (name, colors))
        return getattr(self, name)

def try_parse(value):
    try:    return int(value)
    except: return { 'true': True, 'false': False }.get(value.lower(), value)

def read_config():
    with open('config.cfg', 'r') as cfg_file:
        lines = cfg_file.readlines()
        lines = [
            line.strip().replace(' ', '').split('=')
            for line in lines
            if line.strip() and '=' in line
        ]
        cfg = {key:try_parse(value) for key,value in lines}
        return cfg

cfg = read_config()

NUM_CELLS = cfg.get('CELLS', 100)
RESOLUTION = Resolutions.parse(cfg.get('WINDOW_WIDTH', 1280), cfg.get('WINDOW_HEIGHT', 800))
limit = min(RESOLUTION)
PIXEL_PER_CELL = limit / NUM_CELLS
OFFSET_X = (RESOLUTION.x - (NUM_CELLS * PIXEL_PER_CELL)) / 2
OFFSET_Y = (RESOLUTION.y - (NUM_CELLS * PIXEL_PER_CELL)) / 2

SHOW_FULLSCREEN = cfg.get('FULLSCREEN', False)
SHOW_GRID = cfg.get('SHOW_GRID', True)
BACKGROUND_COLOR = Color.named(cfg.get('BACKGROUND_COLOR', 'black'))
GRID_BACKDROP_COLOR = Color.named(cfg.get('GRID_BACKDROP_COLOR', 'gray'))
GRID_LINE_COLOR = Color.named(cfg.get('GRID_LINE_COLOR', 'black'))
CELL_COLOR = Color.named(cfg.get('CELL_COLOR', 'green'))
CURSOR_COLOR = Color.named(cfg.get('CURSOR_COLOR', 'red'))