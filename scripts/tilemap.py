import pygame as pg
import json

# Defines the offsets to check surrounding tiles for interactions
NEIGHBOR_OFFSET = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0),
                   (0, 1), (1, -1), (1, 0), (1, 1), (-1, 2), (0, 2), (1, 2)]
# Identifies which tiles interact with physics, affecting entities like the player and mobs
PHYSICS_TILES = {"brick", "ground", "random", "random2"}


class Tilemap:
    """
    Represents the tilemap for a game, handling loading, saving, and rendering of tiles.

    Attributes:
        tile_size (int): The size of each tile in pixels.
        tilemap (dict): A dictionary representing the tile layout with positions as keys.
        game (Game): The game instance this tilemap belongs to.
        offgrid_tiles (list): A list of tiles that are placed outside the regular grid.
        randoms (list): Positions of 'random' tiles that can trigger special interactions.
        initial_render (bool): Indicates whether the tilemap has been initially rendered.
    """
    def __init__(self, game, tile_size=16) -> None:
        """
        Initializes a new Tilemap object with a reference to the game instance and a specified tile size.
        
        Args:
            game (Game): The game instance the tilemap belongs to.
            tile_size (int, optional): The size of each tile in pixels. Defaults to 16.
        """
        # Set up the tilemap with a reference to the game instance and default tile size
        self.tile_size = tile_size
        self.tilemap = {}
        self.game = game
        self.offgrid_tiles = []
        self.randoms = []  # Tracks positions for random interactions or items
        self.initial_render = True  # Indicates if the map has been initially rendered

    def tiles_around(self, pos):
        """
        Returns a list of tiles surrounding a specified position to check for collisions or interactions.

        Args:
            pos (tuple): The position around which to check for surrounding tiles.

        Returns:
            list: A list of tiles surrounding the specified position.
        """
        # Return a list of tiles surrounding a specific position to check for collisions or interactions
        tiles = []
        tile_loc = (int(pos[0] // self.tile_size),
                    int(pos[1] // self.tile_size))

        for offset in NEIGHBOR_OFFSET:
            check_loc = str(tile_loc[0] + offset[0]) + \
                ";" + str(tile_loc[1] + offset[1])
            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])
        return tiles

    def save(self, path):
        """
        Saves the current state of the tilemap to a file.

        Args:
            path (str): The file path where the tilemap should be saved.
        """
        # Save the current tilemap to a file for later use or level editing
        with open(path, "w") as file:
            json.dump({"tilemap": self.tilemap, "tilesize": self.tile_size,
                      "offgrid": self.offgrid_tiles}, file)

    def load(self, path):
        """
        Loads a tilemap from a specified file, including tiles and specific entity positions.

        Args:
            path (str): The file path from which to load the tilemap.
        """
        # Load a tilemap from a file, including tiles and specific entity positions
        with open(path, "r") as f:
            file = json.load(f)

            self.tilemap = file["tilemap"]
            self.tile_size = file["tilesize"]
            self.offgrid_tiles = file["offgrid"]

            for x in file["tilemap"]:
                if file["tilemap"][x]["type"] == "random":
                    self.randoms.append(file["tilemap"][x]["pos"])

    def physics_rects_around(self, pos):
        """
        Generates a list of pygame.Rect objects for physics interactions near a given position.

        Args:
            pos (tuple): The position around which to check for physics interaction tiles.

        Returns:
            list: A list of pygame.Rect objects representing tiles that interact with physics.
        """
        # Generate a list of pygame.Rects for physics interactions near a given position
        rects = []
        for tile in self.tiles_around(pos):
            if tile["type"] in PHYSICS_TILES:
                rects.append(pg.Rect(tile["pos"][0] * self.tile_size, tile["pos"]
                             [1] * self.tile_size, self.tile_size, self.tile_size))
        return rects

    def render(self, surf, offset=(0, 0)):
        """
        Renders the tilemap and entities onto a given surface, applying an offset for scrolling.

        Args:
            surf (pygame.Surface): The surface to render the tilemap on.
            offset (tuple): The offset to apply to the tilemap rendering, typically used for scrolling.
        """
        # Render the tilemap and entities onto a given surface, applying an offset for scrolling
        for tile in self.offgrid_tiles:
            if tile["type"] == "koopa" or tile["type"] == "goomba":
                continue  # Exclude enemy entities from general tile rendering
            surf.blit(self.game.assets[tile["type"]], (tile["pos"]
                      [0] - offset[0], tile["pos"][1] - offset[1]))

        for x in range(offset[0] // self.tile_size, (offset[0] + surf.get_width()) // self.tile_size + 1):
            for y in range(offset[1] // self.tile_size, (offset[1] + surf.get_height()) // self.tile_size + 1):
                loc = str(x) + ";" + str(y)
                if loc in self.tilemap:
                    tile = self.tilemap[loc]
                    if tile["type"] == "goomba" or tile["type"] == "koopa":
                        continue  # Again, exclude specific entities to handle them differently
                    if tile["type"] in PHYSICS_TILES:
                        pg.draw.rect(surf, (0, 0, 0), (tile["pos"][0] * self.tile_size - offset[0],
                                     tile["pos"][1] * self.tile_size - offset[1], self.tile_size, self.tile_size))
                    surf.blit(self.game.assets[tile["type"]], (
                        tile["pos"][0] * self.tile_size - offset[0], tile["pos"][1] * self.tile_size - offset[1]))

        self.initial_render = False  # Mark that the initial rendering has been completed
