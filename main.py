import pygame as pg 
import sys
import time


# Import necessary components from other scripts
from scripts.enteties import PhysicsEntity, Player, Randoms, Goomba, Koopa
from scripts.utils import load_image, load_images, Animation

from scripts.tilemap import Tilemap
from scripts.clouds import Clouds


class Game:
    """
    Main class for the game, handling initialization, game loop, and events.
    
    Attributes:
        running (bool): Indicates if the game is currently running.
        display (pygame.Surface): The primary surface for rendering game objects.
        screen (pygame.Surface): The window surface.
        clock (pygame.Clock): Clock used to control game frame rate.
        img (pygame.Surface): The player's image.
        img_pos (list): Position of the player's image.
        movement (list): A boolean list indicating movement directions.
        harmfull_mobs (list): List of all harmful mobs in the game.
        harmless_mobs (list): List of all harmless mobs in the game.
        assets (dict): Dictionary containing all loaded game assets.
        clouds (Clouds): The cloud generator for the game's background.
        player (Player): The player entity.
        scroll (list): The current scrolling offset of the game camera.
        tilemap (Tilemap): The game's tilemap.
        castleX (int): The x position of the castle in the game.
    """

    def __init__(self) -> None:
        """Initializes the game, setting up the window, loading assets, and preparing the game environment."""

        # Initialize game, set up window, and load initial game assets
        pg.init()
        pg.display.set_caption("Mario")
        pg.font.init()
        self.my_font = pg.font.SysFont('Comic Sans MS', 30)
        pg.mixer.init()

        
        self.running = True 
        self.display = pg.Surface((320,240))

        self.screen = pg.display.set_mode((640,480))
        self.clock = pg.time.Clock()

        self.img = pg.image.load("images/mario/small/right/idle/idle.png")
        self.img_pos = [160,260]
        self.movement = [False,False]

        pg.font.init()
        my_font = pg.font.SysFont('Comic Sans MS', 90)


        # Initialize lists to manage different types of game entities
        self.harmfull_mobs = []        
        self.harmless_mobs = []        

        # Load game assets and animations
        self.assets = {
            "brick": load_image("brick.png"),
            "ground": load_image("ground.png"),
            "bush1": load_image("another/bush.png"),
            "bush2": load_image("another/bush2.png"),
            "bush3": load_image("another/bush3.png"),
            "bushes": load_image("another/bushes.png"),
            "clouds": load_image("another/clouds.png"),
            "flower1":load_image("flower/flower1.png"),
            "flower2":load_image("flower/flower2.png"),
            "flower3":load_image("flower/flower3.png"),
            "flower4":load_image("flower/flower4.png"),
            "background": load_image("another/color.png"),
            "clouds": load_images("another/clouds"),
            "coin":Animation(load_images("coins")),
            "random":load_image("another/random/random.png"),
            "sizeup/small/idle":Animation(load_images("sizeup/small")),
            "random2":load_image("another/random/random3.png"),

            "player/small/idle": Animation(load_images("mario/small/right/idle/"), img_dur=4),
            "player/small/run": Animation(load_images("mario/small/right/run"), img_dur=4),
            "player/small/jump": Animation(load_images("mario/small/jump"), img_dur=4),
            "player/big/idle": Animation(load_images("mario/big/right/idle/"), img_dur=4),
            "player/big/run": Animation(load_images("mario/big/right/run"), img_dur=4),
            "player/big/jump": Animation(load_images("mario/big/jump"), img_dur=4),

            "goomba/run": Animation(load_images("goomba/move", (0,255,0)), img_dur=10),

            "koopa/run": Animation(load_images("koopa/right/run",), img_dur=6),
            "shell/shell": Animation(load_images("koopa/dead"), img_dur=10),

            "castle": load_image("castle/castle-1.png", (0,255,0)),
            "koopa":load_image("koopa/right/run/koopa.png"),
            "flag":load_image("flag1.png")
        }


        # Prepare game environment components like clouds and the player
        self.clouds = Clouds(self.assets["clouds"], count=6)
        self.player = Player(self, (50,50), (load_image("mario/small/right/idle/idle.png").get_width()*.8,load_image("mario/small/right/idle/idle.png").get_height()*.9))


        self.scroll = [0,0]
        self.tilemap = Tilemap(self)
        self.castleX = 0


        # Level selection with validation
        try:
            map_input = int(input("velg et map fra en til tre. skriv '1' for map 1. "))
        except ValueError:
            raise Exception("Følg instrugs for valg av map.")
            
        
        if not (map_input == 1 or map_input == 2 or map_input == 3):
            raise Exception("Følg instrugs for valg av map.")
        else:
            # Load selected level and play background music
            self.lvl1 = self.tilemap.load(f"maps/map{map_input}.json")
            pg.mixer.music.load(f'sounds/level{map_input}.mp3')
            pg.mixer.music.play()

        # Initialize game entities based on the tilemap
        for random in self.tilemap.randoms:
            Randoms(self, str(random[0])+";"+str(random[1]))

        for key in self.tilemap.tilemap:
            if self.tilemap.tilemap[key]["type"] == "goomba":
                Goomba(self, (self.tilemap.tilemap[key]["pos"][0]*self.tilemap.tile_size,self.tilemap.tilemap[key]["pos"][1]*self.tilemap.tile_size), (14,14))
            
            elif self.tilemap.tilemap[key]["type"] == "koopa":
                Koopa(self, (self.tilemap.tilemap[key]["pos"][0]*self.tilemap.tile_size,self.tilemap.tilemap[key]["pos"][1]*self.tilemap.tile_size), (14,20))

            elif self.tilemap.tilemap[key]["type"] == "castle":
                self.castleX = self.tilemap.tilemap[key]["pos"][0]*self.tilemap.tile_size

    def handle_events(self):
        """Handles input events, including keyboard and mouse inputs, to control the game state."""

        # Process input events to control player movement and actions
        for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_LEFT:
                        self.movement[0] = True
                    if event.key == pg.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pg.K_UP or event.key == pg.K_SPACE:
                        if self.player.jump_count <= 1:
                            self.player.velocity[1] = -3
                            self.player.jump_count += 1
                            pg.mixer.Sound('sounds/jump.ogg').play()

                if event.type == pg.KEYUP:
                    if event.key == pg.K_LEFT:
                        self.movement[0] = False
                    if event.key == pg.K_RIGHT:
                        self.movement[1] = False

    def adjust_cam(self):
        """
        Adjusts the camera scroll based on the player's position to ensure the player remains in view.
        
        Returns:
            tuple: The adjusted camera scroll position.
        """

        # Adjust camera scroll based on player position to keep player in view
        self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
        self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
        return (int(self.scroll[0]), int(self.scroll[1]))
    
    def update(self):
        """Updates the game state, including cloud movements, mob updates, player updates, and checks for game end conditions."""

        # Update all mobs
        self.clouds.update()
        for mob in self.harmless_mobs: mob.update(self.tilemap)
        for mob in self.harmfull_mobs: mob.update(self.tilemap)
        self.player.update(self.tilemap, (self.movement[1]-self.movement[0],0))

        # Check for win or loss
        if self.player.pos[1] > 30*16:
            self.defeat()
        if self.player.pos[0] > self.castleX:
            self.victory()

    def victory(self):
        """Handles the victory condition, displaying the victory screen and ending the game."""

        # Display victory screen and end game
        self.display.blit(self.assets["background"], (0,0))
        text_surface = self.my_font.render('Victory', False, (0, 255, 0))
        self.display.blit(text_surface, (0,0))
        self.display.blit(load_image("sizeup/small/01sizeup.png"), (130,10))
        self.screen.blit(pg.transform.scale(self.display,self.screen.get_size()),(0,0))

        pg.display.update()
        time.sleep(3)
        self.running = False


    def defeat(self):
        """Handles the defeat condition, displaying the defeat screen and ending the game."""

        # Display defeat screen and end game
        pg.mixer.music.pause()
        pg.mixer.Sound('sounds/gameover.ogg').play() # play defeat screen sound
        self.display.blit(self.assets["background"], (0,0))
        text_surface = self.my_font.render('Defeat', False, (255, 0, 0))
        self.display.blit(text_surface, (0,0))
        img = load_image("koopa/right/run/koopa.png")
        self.display.blit(img, (130,10))

        self.screen.blit(pg.transform.scale(self.display,self.screen.get_size()),(0,0))
        pg.display.update()

        time.sleep(3)
        self.running = False
        

    def render(self, render_scroll):
        """
        Renders the game entities and environment to the display surface.

        Args:
            render_scroll (tuple): The current scroll offset for rendering.
        """
        
        # Render game entities and environment
        self.clouds.render(self.display, offset=render_scroll)
        self.tilemap.render(self.display, offset=render_scroll)

        self.player.render(self.display, offset=render_scroll)

        for mob in self.harmfull_mobs: mob.render(self.display, offset=render_scroll)
        for mob in self.harmless_mobs: mob.render(self.display, offset=render_scroll)


    def run(self):
        """The main game loop, running the game until the `running` attribute is False."""

        # Main game loop
        while self.running:
            self.display.blit(self.assets["background"], (0,0))

            render_scroll = self.adjust_cam()

            self.update()
            self.render(render_scroll)

            self.handle_events()
            
            self.screen.blit(pg.transform.scale(self.display,self.screen.get_size()),(0,0))

            pg.display.update()
            self.clock.tick(60)

Game().run()