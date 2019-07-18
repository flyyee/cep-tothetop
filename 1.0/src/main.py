import pygame as pg
import sys
from settings import *
from sprites import *
from tilemap import *
import random
from datetime import datetime



class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((1024, 768), pg.FULLSCREEN)
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.load_data()  # generates map
        # loop music
        pg.mixer.music.load("./assets/moose.mp3")
        pg.mixer.music.set_volume(0.3)
        pg.mixer.music.play(-1)

    def load_data(self):
        self.bgimage = pg.image.load('./assets/trianglify.png')
        self.bgrect = self.bgimage.get_rect()

    def new(self):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.Group()  # all sprites
        self.walls = pg.sprite.Group()  # all sprites with collision
        self.spikes = pg.sprite.Group()  # all sprites that will kill you
        self.lasers = pg.sprite.Group()  # all sprites that will kill you that need animation
        self.levels = []  # 2d list of levels, filled later
        leveltype1 = ["w", "w", "w", "w", "w", "w", "", "", "", "", "", "", "w", "w", "w", "w"]
        leveltype2 = ["", "", "", "", "", "w", "", "", "", "", "", "", "w"]
        # creates data for levels
        data = [["w","w","w","w","w","w","w","w","w","w","w","w","w","w","w","w"],
                         ["","","","","","","","p"],
                         leveltype1,leveltype2,
                         leveltype1, leveltype2,
                         leveltype1, leveltype2,
                         leveltype1, leveltype2,
                         leveltype1, leveltype2,
                         leveltype1, []
                         ]

        for row, tiles in enumerate(data):
            self.levels.append([])  # creates new level within the list of levels
            for col, tile in enumerate(tiles):
                # appends sprites to current level
                if tile == 'w':
                    self.levels[row].append(Wall(self, col, row))
                if tile == 'b':
                    self.levels[row].append(Wall(self, col, row, draw=False))
                if tile == 'x':
                    self.levels[row].append(Wall(self, col, row, spike=True))
                if tile == 'p':
                    self.player = Player(self, col, row)

        # sets up more settings
        self.camera = Camera(WIDTH, HEIGHT)
        self.leveltype = 0  # determines type of level to be generated (position of lasers)
        self.levelstonewlevel = 3  # number of levels from current top level to a new level
        # will be set randomly later
        self.prevypos = self.player.pos[1]  # player's previous y coordinate
        self.levelspikes = False  # determines whether level generated will have spikes
        # will be set randomly later

        # determines length of lasers in level
        self.laser1length = 0
        self.laserlength = 0
        self.laser2length = 0

        # determines length of walls in level
        self.wall1length = 0
        self.wall2length = 0
        self.walllength = 0


        self.newleveltime = 0  # when this time is met, the game is sped up

    def run(self):
        # game loop - set self.playing = False to end the game
        self.seed = datetime.now()  # generates a seed to be used for generating random number
        # using the current date and time

        newseed = ""

        for x in str(self.seed):  # makes seed look cooler
            if x in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                # print("number")
                # print(x)
                chars = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]
                newseed += chars[int(x)]
            elif x == "-":
                newseed += "k"
            elif x == " ":
                newseed += "l"
            elif x == ":":
                newseed += "m"
            elif x == ".":
                newseed += "n"

        self.seed = newseed

        random.seed(self.seed)

        starttime = pg.time.get_ticks()  # gets current time, to be used in determining score later
        self.playing = True  # runs game until quit signal is sent
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()
        endtime = pg.time.get_ticks()
        # returns score
        return int(((endtime - starttime) / 2500) ** 1.1) * 1000 + random.randint(0, 999)
        # appends a random number from 0 to 1000 to encourage new players

    # convenience function that randomly generates laser set-ups based on the input length
    def laserboy(self, ll, start):
        # lol no algo
        if ll == 2:
            return [laser(self, start, 12, 2)]
        elif ll == 3:
            return [laser(self, start, 12, 3)]
        elif ll == 4:
            return self.laserboy(2, start) + self.laserboy(2, start + 2)
        elif ll == 5:
            whatdoido = random.randint(0, 1)
            if whatdoido == 0:
                return self.laserboy(2, start) + self.laserboy(3, start + 2)
            else:
                return self.laserboy(3, start) + self.laserboy(2, start + 3)
        elif ll == 6:
            whatdoido = random.randint(0, 1)
            if whatdoido == 0:
                return self.laserboy(3, start) + self.laserboy(3, start + 3)
            else:
                return self.laserboy(2, start) + self.laserboy(4, start + 2)
        elif ll == 7:
            whatdoido = random.randint(0, 1)
            if whatdoido == 0:
                return self.laserboy(4, start) + self.laserboy(3, start + 4)
            elif whatdoido == 1:
                return self.laserboy(5, start) + self.laserboy(2, start + 5)

        elif ll == 8:
            whatdoido = random.randint(0, 1)
            if whatdoido == 0:
                return self.laserboy(5, start) + self.laserboy(3, start + 5)
            else:
                return self.laserboy(6, start) + self.laserboy(2, start + 6)
        elif ll == 9:
            whatdoido = random.randint(0, 2)
            if whatdoido == 0:
                return self.laserboy(3, start) + self.laserboy(3, start + 3) + self.laserboy(3, start + 6)
            elif whatdoido == 1:
                return self.laserboy(2, start) + self.laserboy(7, start + 2)
            else:
                return self.laserboy(7, start) + self.laserboy(2, start + 7)
        elif ll == 10:
            whatdoido = random.randint(0, 2)
            if whatdoido == 0:
                return self.laserboy(4, start) + self.laserboy(6, start + 4)
            elif whatdoido == 1:
                return self.laserboy(5, start) + self.laserboy(5, start + 5)
            else:
                return self.laserboy(3, start) + self.laserboy(3, start + 3) + self.laserboy(4, start + 6)
        print("thisisbad134")
        return "THISISBAD134"  # don't worry this never happens

    def update(self):
        # update portion of the game loop

        if self.player.update() == 96:  # player is dead
            self.playing = False  # sends stop signal to stop game loop

        toremove = []
        toadd = []

        for l in self.lasers.sprites():
            val = l.update()
            if val == 777:
                # gets lasers that are currently inactive (based on return value)
                # appends to the list for removal from the list of spikes
                # (sprites that will kill you) later
                # cannot be removed while iterating over the list
                toremove.append(l)
            elif val == 666:
                # gets lasers that are currently active (based on return value)
                # appends to the list for adding to the list of spikes
                # (sprites that will kill you) later
                # cannot be removed while iterating over the list
                toadd.append(l)

        for l in toremove:
            self.spikes.remove(l)  # removes death on collision property

        for l in toadd:
            self.spikes.add(l)

        self.prevypos = self.player.rect.y  # re-adds death on collision property


        if self.camera.bestupdate() == 69:  # camera has moved down one space
            # aka generate a new level on top (because it is entering frame soon)
            # and destroy bottom level (because it is out of frame)
            for sprite in self.levels[0]:  # destroys old level
                sprite.kill()  # removes sprite from all groups
                del sprite  # saves memory by deleting unused sprites from memory

            for x in range(1, 13):  # moves each level down by one to make room for the new level
                # sort of like a conveyor belt system where every time the camera moves down by one square
                # or one level, the bottom level is removed and the top level is added
                # all while the rest of the levels continue moving downwards for the cycle to continue
                self.levels[x - 1] = self.levels[x]

            self.levels[12] = []  # creates new level, that is not currently in frame
            # but will enter the frame soon

            if self.levelspikes:
                # generates spikes if there are spikes to be generated for the level
                self.levelspikes = False
                # checks type of level whether the level consists of
                # a laser sandwiched between two walls WWWWWWLLLLLWWWWWW or
                # a wall sandwiched between two lasers LLLLLWWWWWLLLLLLL
                if self.leveltype == 1:
                    # aka wall laser wall
                    for x in range(self.wall1length):
                        self.levels[12].append(Wall(self, x, 12, spike=True))
                    for x in range(self.wall2length):
                        self.levels[12].append(Wall(self, x + self.wall1length + self.laserlength, 12, spike=True))
                else:
                    # aka laser wall laser
                    for x in range(self.walllength):
                        self.levels[12].append(Wall(self, x + self.laser1length, 12, spike=True))

            if self.levelstonewlevel == 0:
                # if next level is a new level, randomly generate settings for lasers
                if (random.randint(0, 1)) == 1:  # determines whether the level has spikes
                    self.levelspikes = True
                if self.levelspikes:
                    # more space for maneuvering for levels with spikes
                    self.levelstonewlevel = random.randint(3, 6)
                else:
                    self.levelstonewlevel = random.randint(2, 5)

                if self.leveltype == 0:  # generates new level
                    # aka wall laser wall
                    self.laserlength = random.randint(3, 8)
                    self.wall1length = random.randint(4, 7)
                    self.wall2length = 16 - self.laserlength - self.wall1length
                    for x in range(self.wall1length):
                        self.levels[12].append(Wall(self, x, 12))
                    for x in range(self.wall2length):
                        self.levels[12].append(Wall(self, x + self.laserlength + self.wall1length, 12))

                    # how long each laser is active and inactive for on each level is the same
                    # randomly generated value
                    thislvllasers = self.laserboy(self.laserlength, self.wall1length)
                    safetime = random.uniform(0.5, 3.5)
                    unsafetime = random.uniform(1.5, 2.5) + safetime

                    for las in thislvllasers:
                        las.safetime = safetime
                        las.unsafetime = unsafetime
                    self.levels[12].extend(thislvllasers)

                else:
                    # aka laser wall laser
                    self.walllength = random.randint(3, 7)
                    self.laser1length = random.randint(3, 7)
                    self.laser2length = 16 - self.walllength - self.laser1length
                    for x in range(self.walllength):
                        self.levels[12].append(Wall(self, self.laser1length + x, 12))

                    safetime = random.uniform(0.5, 3.5)
                    unsafetime = random.uniform(1.5, 2.5) + safetime

                    thislvllasers1 = self.laserboy(self.laser1length, 0)

                    for las in thislvllasers1:
                        las.safetime = safetime
                        las.unsafetime = unsafetime
                    self.levels[12].extend(thislvllasers1)

                    thislvllasers2 = self.laserboy(self.laser2length, self.walllength + self.laser1length)

                    for las2 in thislvllasers2:
                        las2.safetime = safetime
                        las2.unsafetime = unsafetime
                    self.levels[12].extend(thislvllasers2)

                self.leveltype = 1 - self.leveltype

            else:
                self.levelstonewlevel -= 1  # decreases number of levels to new level by one

            if self.camera.automove < 10:  # while camera speed is not at the max speed of 10
                if pg.time.get_ticks() > self.newleveltime:  # when the time newleveltime is past
                    self.newleveltime = pg.time.get_ticks() + 8 * self.camera.automove * 1000
                    # creates a newleveltiem that increases as the camera speed increases
                    self.camera.automove += 1

    def draw(self):
        self.screen.fill(BGCOLOR)
        self.screen.blit(self.bgimage, self.bgrect)
        # draws all sprites
        for lvl in self.levels:
            for sprite in lvl:
                if self.all_sprites in sprite.groups:  # only draws opaque blocks
                    # only draws if sprite belongs to all sprites
                    self.screen.blit(sprite.image, self.camera.newapply(sprite))
        self.screen.blit(self.player.image, self.camera.newapply(self.player))

        pg.display.flip()

    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

    def menu(self, score=-1):
        # creates a nice looking menu with layers

        # bottom layer is background image
        bgimage = pg.image.load('./assets/trianglify.png')
        bgrect = bgimage.get_rect()
        self.screen.blit(bgimage, bgrect)

        # layer over bottom layer is a solid color fill to mask the background image
        aa = pg.Surface((WIDTH, HEIGHT))
        aa.fill((80, 100, 80))
        aa.set_alpha(70)
        self.screen.blit(aa, aa.get_rect())

        font = pg.font.SysFont('Calibri', 70)  # sets the font

        # layer over mask is the score or title
        if score != -1:  # if a score is passed to the function
            text = font.render("Score: " + str(score), True, (0,0,0))
            textrect = text.get_rect()
            textrect.center = ((WIDTH / 2), (HEIGHT / 2) - 230)
            self.screen.blit(text, textrect)
            text = font.render("Seed: " + str(self.seed), True, (0,0,0))
        else:  # no score is passed, aka game was just launched
            text = font.render("XTFPB", True, (150,50,150))

        textrect = text.get_rect()
        textrect.center = ((WIDTH / 2), (HEIGHT / 2) - 150)
        self.screen.blit(text, textrect)

        # creates translucent surface for the buttons
        trans = pg.Surface((WIDTH, HEIGHT))
        trans.set_colorkey((0, 0, 0))
        trans.set_alpha(60)
        playbutton = pg.draw.circle(trans, (0, 255, 0), (400, 500), 90, 0)
        exitbutton = pg.draw.circle(trans, (255, 100, 100), (650, 500), 90, 0)

        # layer of opaque button outlines over the mask
        pg.draw.circle(self.screen, (0, 0, 0), (400, 500), 90, 1)  # opaque border
        pg.draw.circle(self.screen, (0, 0, 0), (650, 500), 90, 1)

        # layer of translucent buttons over the mask
        self.screen.blit(trans, trans.get_rect())

        # layers of button text over the buttons
        text = font.render("PLAY", True, (0,0,0))
        textrect = text.get_rect()
        textrect.center = playbutton.center
        self.screen.blit(text, textrect)

        text = font.render("EXIT", True, (0,0,0))
        textrect = text.get_rect()
        textrect.center = exitbutton.center
        self.screen.blit(text, textrect)

        pg.display.update()

        startplaying = False
        while not startplaying:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    quit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    if playbutton.collidepoint(pg.mouse.get_pos()):
                        startplaying = True
                    if exitbutton.collidepoint(pg.mouse.get_pos()):
                        pg.quit()
                        quit()

# create the game object
g = Game()

g.new()
g.menu()

while True:
    g.menu(g.run())
    g.new()