import pygame as pg
import sys

# Import necessary components from other scripts
from scripts.enteties import PhysicsEntity, Player
from scripts.utils import load_image, load_images, Animation
from scripts.tilemap import Tilemap

RENDER_SCALE = 2.0


class Editor:
    def __init__(self) -> None:
        # Initialize the editor, setting up the window and loading assets
        pg.init()
        pg.display.set_caption("editor")
        self.running = True
        self.display = pg.Surface((320, 240))

        self.screen = pg.display.set_mode((640, 480))
        self.clock = pg.time.Clock()

        # Initialize the tilemap for the level being edited
        self.tilemap = Tilemap(self)

        self.img = pg.image.load("images/mario/small/right/idle/idle.png")
        self.img_pos = [160, 260]
        self.movement = [False, False]
        self.jump_count = 0

        # Load game assets that can be placed in the level
        self.assets = {
            "brick": load_image("brick.png"),
            "ground": load_image("ground.png"),
            "bush1": load_image("another/bush.png"),
            "bush2": load_image("another/bush2.png"),
            "bush3": load_image("another/bush3.png"),
            "bushes": load_image("another/bushes.png"),
            "random": load_image("another/random/random.png"),
            "castle": load_image("castle/castle.png"),
            "koopa": load_image("koopa/right/run/koopa.png"),
            "goomba": load_image("goomba/run/goombs1.png"),
            "flag": load_image("flag1.png"),
            "flower1": load_image("flower/flower1.png"),
            "flower2": load_image("flower/flower2.png"),
            "flower3": load_image("flower/flower3.png"),
            "flower4": load_image("flower/flower4.png"),


        }

        # Movement and camera control variables
        self.movement = [False, False, False, False]
        self.scroll = [0, 0]
        self.tilemap = Tilemap(self)
        self.tile_list = list(self.assets)
        self.tile_group = 0
        self.tile_variant = 0
        self.clicking = False
        self.right_clicking = False
        self.shift = False
        self.ongrid = True
        self.mpos = [0, 0]

    def handle_events(self):
        # Process input events to control the editor and modify the level
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            # Mouse and keyboard event handling for editing commands
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.clicking = True
                    if not self.ongrid:
                        self.tilemap.offgrid_tiles.append({"type": self.tile_list[self.tile_group], "pos": (
                            self.mpos[0] + self.scroll[0], self.mpos[1] + self.scroll[1])})

                if event.button == 3:
                    self.right_clicking = True
                if event.button == 4:
                    self.tile_group = (self.tile_group -
                                       1) % len(self.tile_list)
                if event.button == 5:
                    self.tile_group = (self.tile_group +
                                       1) % len(self.tile_list)

            if event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    self.clicking = False
                if event.button == 3:
                    self.right_clicking = False

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_s:
                    self.tilemap.save("map2.json")
                if event.key == pg.K_LEFT:
                    self.movement[0] = True
                if event.key == pg.K_RIGHT:
                    self.movement[1] = True
                if event.key == pg.K_UP:
                    self.movement[2] = True
                if event.key == pg.K_DOWN:
                    self.movement[3] = True
                if event.key == pg.K_g:
                    self.ongrid = not self.ongrid
                if event.key == pg.K_LSHIFT:
                    self.shift == True

            if event.type == pg.KEYUP:
                if event.key == pg.K_LEFT:
                    self.movement[0] = False
                if event.key == pg.K_RIGHT:
                    self.movement[1] = False
                if event.key == pg.K_UP:
                    self.movement[2] = False
                if event.key == pg.K_DOWN:
                    self.movement[3] = False

    def adjust_cam(self):
        # Adjust the camera based on player movement (not used in the editor context)
        self.scroll[0] += (self.player.rect().centerx -
                           self.display.get_width() / 2 - self.scroll[0]) / 30
        self.scroll[1] += (self.player.rect().centery -
                           self.display.get_height() / 2 - self.scroll[1]) / 30
        return (int(self.scroll[0]), int(self.scroll[1]))

    def run(self):
        # Main loop for running the editor
        while self.running:
            self.display.fill((0, 0, 0))  # Clear the display each frame

            # Update camera scroll based on keyboard movement
            self.scroll[0] += (self.movement[1] - self.movement[0]) * 2
            self.scroll[1] += (self.movement[3] - self.movement[2]) * 2

            # Render the current state of the tilemap
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            self.tilemap.render(self.display, offset=render_scroll)

            # Display the currently selected tile at the mouse position
            current_tile_img = self.assets[self.tile_list[self.tile_group]].copy(
            )
            current_tile_img.set_alpha(100)

            # Adjust mouse position based on render scale and display the tile accordingly
            self.mpos = pg.mouse.get_pos()
            self.mpos = (self.mpos[0] / RENDER_SCALE,
                         self.mpos[1] / RENDER_SCALE)
            tile_pos = (int((self.mpos[0] + self.scroll[0]) // self.tilemap.tile_size), int(
                self.mpos[1] + self.scroll[1]) // self.tilemap.tile_size)

            # Handle placing and removing tiles with mouse clicks
            if self.ongrid:
                self.display.blit(current_tile_img, (tile_pos[0] * self.tilemap.tile_size -
                                  self.scroll[0], tile_pos[1] * self.tilemap.tile_size - self.scroll[1]))
            elif not self.ongrid:
                self.display.blit(current_tile_img, self.mpos)

            if self.clicking and self.ongrid:
                self.tilemap.tilemap[str(tile_pos[0]) + ";" + str(tile_pos[1])] = {
                    "type": self.tile_list[self.tile_group], "pos": tile_pos}
            if self.right_clicking:
                tile_loc = str(tile_pos[0]) + ";" + str(tile_pos[1])
                if tile_loc in self.tilemap.tilemap:
                    del self.tilemap.tilemap[tile_loc]
                for tile in self.tilemap.offgrid_tiles.copy():
                    tile_img = self.assets[tile["type"]]
                    tile_r = pg.Rect(tile["pos"][0] - self.scroll[0], tile["pos"][1] -
                                     self.scroll[1], tile_img.get_width(), tile_img.get_height())
                    if tile_r.collidepoint(self.mpos):
                        self.tilemap.offgrid_tiles.remove(tile)

            # Update the display and cap the frame rate
            self.display.blit(current_tile_img, (5, 5))
            self.handle_events()
            self.screen.blit(pg.transform.scale(
                self.display, self.screen.get_size()), (0, 0))

            pg.display.update()
            self.clock.tick(60)


# Create and run the editor instance
Editor().run()
