import pygame as pg
from settings import *

class Camera:
    def __init__(self, width, height):
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.automove = 2  # the speed at which the camera moves down
        self.currentautomove = 0  # total amount of automove so far
        # used in determining when to spawn a new level later

    def newapply(self, entity):
        entity.rect = entity.rect.move(0, self.automove)
        return entity

    def bestupdate(self, newautomove=0):  # accepts a new automove to change the set automove
        if newautomove == 0:
            self.currentautomove += self.automove
        else:
            self.automove = newautomove  # changes the automove in necessary
            self.currentautomove += self.automove

        if self.currentautomove > 64:
            # if sum of total automove so far is more than the length of a square
            # aka camera has moved down by one level, so call for
            # spawning a new level and destroying the previous level
            self.currentautomove %= 64
            return 69