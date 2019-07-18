import pygame as pg
from settings import *
from math import sqrt
import numpy
vec = pg.math.Vector2

class Player(pg.sprite.Sprite):  # player class
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.vel = vec(0, 0)
        self.pos = vec(x, 11 - y) * TILESIZE
        # input y value is flipped and is an array value
        # so the actual value is 12 - (y + 1) or 11 - y
        # then gets the actual coordinates by multiplying with tilesize
        self.vel = vec(0, 0)
        self.dy = 0

        # mouse settings for use in movement later
        self.mousestartpos = vec(0, 0)  # position of mouse click
        self.mousestarttime = pg.time.get_ticks()  # duration of mouse hold
        self.waitingformouserelease = False  # whether mouse is currently being held

    def get_keys(self):
        if not self.waitingformouserelease:  # if mouse button is not being held at the moment
            # only checks if mouse is not currently being pressed to identify new presses
            if pg.mouse.get_pressed()[0]:  # checks if left mouse button is clicked
                self.waitingformouserelease = True  # indicates mouse button is being held moment
                self.mousestartpos = (pg.mouse.get_pos()[0], pg.mouse.get_pos()[1])
                # gets mouse click position into a vector
                self.mousestarttime = pg.time.get_ticks()
                # gets current time to record start time of mouse click
        else:  # waiting for mouse release:
            if not pg.mouse.get_pressed()[0]:  # left mouse button not being held, aka released
                mouseendpos = vec(pg.mouse.get_pos()[0], pg.mouse.get_pos()[1])
                # gets end position of mouse release into a vector
                mouseendtime = pg.time.get_ticks()
                # gets current time to record end time of mouse click
                dx = mouseendpos[0] - self.mousestartpos[0]  # distance travelled on x axis
                dy = mouseendpos[1] - self.mousestartpos[1]  # distance travelled on y axis
                self.dx = dx
                self.dy = dy
                d = mouseendpos.distance_to(self.mousestartpos)
                # using pythagoras' theorem to calculate the distance
                # between mouse click and mouse release positions
                t = mouseendtime - self.mousestarttime  # time mouse was held
                v = (d / t) ** 2  # determines velocity according to a cool formula i made up
                # scales exponentially so slow speeds are penalised more and faster speeds are rewarded more
                if dx == 0:  # prevents divide by zero error
                    self.vel.x = 0
                else:
                    # gets actual velocity according to another cool formula i made up
                    self.vel.x = (dx / abs(dx)) * sqrt(abs(dx)) * v  # avoid imaginary numbers while keeping direction
                if dy == 0:  # prevents divide by zero error
                    self.vel.y = 0
                else:
                    # gets actual velocity according to another cool formula i made up
                    self.vel.y = (dy / abs(dy)) * sqrt(abs(dy)) * v * 1.5
                    # scales by 1.5 because moving mouse up/down is harder that left/right
                self.waitingformouserelease = False  # starts accepting mouse input again

        self.vel.y += 9.81  # gravity

    def collide_with_walls(self, dir):
        if dir == 'x':
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            # gets list of wall objects colliding with player
            if hits:
                # produces collision based on direction of movement
                if self.vel.x > 0:
                    self.pos.x = hits[0].rect.left - self.rect.width
                if self.vel.x < 0:
                    self.pos.x = hits[0].rect.right

                # reverses movement in opposite direction and scales it up
                self.vel.x = -self.vel.x * 1.1
                self.rect.x = self.pos.x

            # collision with right side of screen
            if self.rect.x + self.rect.width >= 1024:
                self.pos.x = 1024 - self.rect.width
                self.vel.x = -self.vel.x * 1.1
                self.rect.x = self.pos.x

            # collision with left side of screen
            if self.rect.x <= 0:
                self.pos.x = 0
                self.vel.x = -self.vel.x
                self.rect.x = self.pos.x

        if abs(self.vel.x) > 1024:  # speed limit
            self.vel.x = abs(self.vel.x) / self.vel.x * 1024
            # maintains direction (negativity/positivity)

        if dir == 'y':
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            # gets walls colliding with player
            if hits:
                # deals with collisions according to direction
                if self.vel.y < 0:
                    self.pos.y = hits[0].rect.bottom

                if self.vel.y > 0:
                    if hits[0].rect.bottom - self.game.camera.automove <= self.rect.y:
                        # this is an edge case that happens when the player is falling
                        # but the game is moving down faster than the fall speed
                        # causing the player to collide with the underside of a wall
                        # while moving downwards
                        self.pos.y += self.game.camera.automove * 2
                        self.vel.y = 9.81 * 100  # resolved with bouncy surface on the bottom of walls
                    else:
                        self.pos.y = hits[0].rect.top - self.rect.height

                # makes moving up slightly harder
                self.vel.y = -self.vel.y + 0.1 * (abs(self.vel.y))
                self.rect.y = self.pos.y

            # collision with top of screen
            if self.rect.y <= 0:
                self.pos.y = 0
                self.vel.y = -self.vel.y
                self.rect.y = self.pos.y


            # collision with bottom of game
            if self.rect.y + self.rect.width >= 768:
                return 421  # indicates player has fallen to his death

        if abs(self.vel.y) > 768:  # speed limit
            self.vel.y = abs(self.vel.y) / self.vel.y * 768

    def spikescollide(self):
        hits = pg.sprite.spritecollide(self, self.game.spikes, False)
        if hits:
            self.vel.x = 0
            self.vel.y = 0
            return 422  # indicates player is dead on contact with a spike object


    def update(self):
        self.get_keys()
        self.pos += self.vel * self.game.dt
        self.rect.x = self.pos.x
        self.collide_with_walls('x')
        self.rect.y = self.pos.y

        # returns that player is dead if any of the following death signals are met
        if self.collide_with_walls('y') == 421:
            return 96
        if self.spikescollide() == 422:
            return 96


class Wall(pg.sprite.Sprite):  # wall class
    # big parent class for all objects with collisions, including deadly objects
    def __init__(self, game, x, y, draw=True, spike=False, laser2=False, laser3=False):
        # gets type of wall
        self.image = pg.Surface((TILESIZE, TILESIZE))
        if spike:
            self.groups = game.all_sprites, game.spikes
            self.image = pg.image.load("./assets/spike.png").convert_alpha()
        elif laser2:  # laser that spans two squares
            self.groups = game.all_sprites, game.spikes
            self.image = pg.image.load("./assets/laser2.png").convert_alpha()
        elif laser3:  # laser that spans three squares
            self.groups = game.all_sprites, game.spikes
            self.image = pg.image.load("./assets/laser3.png").convert_alpha()
        elif draw:  # basic green wall
            self.groups = game.all_sprites, game.walls
            self.image.fill(GREEN)
            # adds a bouncy surface rectangle to the bottom of all basic walls
            imgrect = self.image.get_rect()
            bottom = pg.Surface((imgrect.width, 14))
            bottom.fill((50, 100, 69))
            bottomrect = bottom.get_rect()
            bottomrect.y = 50
            self.image.blit(bottom, bottomrect)
        else:  # does not draw
            self.groups = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        self.rect = self.image.get_rect()
        self.x = x
        self.y = 11 - y  # flips input y value
        self.rect.x = x * TILESIZE
        self.rect.y = (11 - y) * TILESIZE


class laser(pg.sprite.Sprite):
# subclass of wall that includes only lasers
    def __init__(self, game, x, y, type):
        self.groups = game.all_sprites, game.spikes, game.lasers
        # converts alpha so alpha can be manipulated later
        if type == 2:
            self.image = pg.image.load("./assets/laser2.png").convert_alpha()
        elif type == 3:
            self.image = pg.image.load("./assets/laser3.png").convert_alpha()

        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        self.rect = self.image.get_rect()
        self.x = x
        self.y = 11 - y  # flips y value
        self.rect.x = x * TILESIZE
        self.rect.y = (11 - y) * TILESIZE

        # internal clock to time change of states (alpha and colour)
        self.clock = pg.time.Clock()
        self.currenttime = 0.0

        # determine whether or not to apply the one time change of state, used later
        self.updatereset = True
        self.nearlyreset = True

    def change_alpha(self, alpha):
        # img = self.image
        chan = pg.surfarray.pixels_alpha(self.image)  # aka an array of every pixel's alpha
        # aka either 0 (transparent) (the background)
        # or 255 (opaque) (the image)
        chan2 = numpy.minimum(chan, numpy.ones(chan.shape, dtype=chan.dtype)) * alpha
        # numpy.ones(chan.shape, dtype=chan.dtype) is an array full of 1s the size of the surfarray
        # chan2 takes the minimum of the ones and the surfarray
        # so if a pixel is transparent aka alpha = 0, when compared to the value 1 from the ones, it will be chosen
        # if a pixel is not transparent aka alpha > 0 (maybe 100 or 255), when compared to the value of 1, 1 will be chosen
        # the end result is an array that is either 0 or 1, where 1 represents that it was not transparent in the past
        # then all values in the end array is multiplied by the ideal alpha
        # this produces an array maintaining the pixels that were previously transparent,
        # while changing the alpha of all the non-transparent pixels to a set value
        # this is because when the 0 is multiplied by the value, it remains 0, aka transparent
        # but when the value of 1 is multiplied by the value, the alpha is saved at that non-transparent value
        numpy.copyto(chan, chan2)
        del chan

    def update(self):
        self.clock.tick()
        # keeps track of time elapsed
        self.currenttime += self.clock.get_time() / 1000

        if self.updatereset:  # resets laser surface to be transparent and completely yellow
            self.updatereset = False
            self.change_alpha(2)
            arr = pg.surfarray.pixels3d(self.image)
            # makes color of laser completely yellow
            arr[:, :, 0] = 255  # r
            arr[:, :, 1] = 255  # g
            arr[:, :, 2] = 0  # b

        if self.currenttime > self.safetime:  # laser is activated
            if self.nearlyreset:  # sets these only for the first time
                # makes laser copmletely red and opaque
                self.nearlyreset = False
                self.change_alpha(255)
                arr = pg.surfarray.pixels3d(self.image)
                arr[:, :, 1] = 0

            if self.currenttime > self.unsafetime:  # laser is safe again
                self.currenttime = 0.0  # resets internal time
                self.updatereset = True
                self.nearlyreset = True

            return 666
        else:
            # laser starts to glow orange and more opaque
            if self.currenttime < 2.0:
                val = 2 + (self.currenttime - 0.5) * 85
                if val > 2:
                    self.change_alpha(int(val))  # increases alpha slowly
                else:
                    self.change_alpha(2)

                arr = pg.surfarray.pixels3d(self.image)
                arr[:, :, 1] -= 1  # g
                # makes color redder and less yellow

            return 777