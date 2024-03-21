import pygame as pg
import random as rd


class PhysicsEntity():
    """
    A base class for all entities in the game that have physical interactions.
    
    Attributes:
        game (Game): The game instance this entity belongs to.
        type (str): The type of the entity (e.g., 'player', 'goomba').
        pos (list): The position of the entity on the screen.
        size (list): The size of the entity.
        velocity (list): The velocity of the entity.
        can_collide (bool): Indicates if the entity can participate in collision detection.
        mob_types (list): A list of entity types considered as mobs.
        recovering_blink (int): Counter used for the blinking effect during recovery.
        action (str): The current action of the entity (e.g., 'idle', 'run').
        anim_offset (tuple): The offset for the animation rendering.
        flip (bool): Indicates if the entity's image should be flipped horizontally.
    """
    # Base class for all entities with physical interactions in the game
    def __init__(self, game, e_type, pos, size) -> None:
        """Initializes the PhysicsEntity with the game instance, type, position, and size."""
        # Initialize basic properties for physical entities
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = [size[0], size[1]]
        self.velocity = [0, 0]  # Movement vector
        self.can_colide = True  # Determines if entity participates in collision detection
        # Types of entities considered as mobs
        self.mob_types = ["goomba", "koopa", "shell"]
        self.recovering_blink = 0  # Used for blinking effect during recovery

        self.action = ""
        self.anim_offset = (-3, -3)
        self.flip = False

        # Set initial animation based on entity type
        if self.type == "player":
            self.set_action("small/idle")
        elif self.type == "goomba" or self.type == "koopa":
            self.set_action("run")
        elif self.type == "sizeup":
            self.set_action("small/idle")
        elif self.type == "shell":
            self.set_action("shell")

    def set_action(self, action):
        """
        Sets the current action for the entity and updates its animation accordingly.
        
        Args:
            action (str): The action to set for the entity.
        """
        # Change the current action and update the animation accordingly
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type +
                                              "/" + self.action].copy()

    def rect(self):
        """
        Creates a pygame.Rect for the entity based on its position and size for collision detection.
        
        Returns:
            pygame.Rect: The Rect object for the entity.
        """
        # Generate a pygame.Rect for collision detection
        return pg.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def update(self, tilemap, movement=(0, 0)):
        """
        Updates the entity's state, including its position, collisions, and animation.
        
        Args:
            tilemap (Tilemap): The game's tilemap for checking collisions.
            movement (tuple): The desired movement direction for the entity.
        """

        # Update entity state, including position, collisions, and animations
        # Handle vertical and horizontal movements separately for precise collision detection
        vertical_collision_mob, vertical_collision_player = False, False
        self.collisions = {"up": False, "down": False,
                           "left": False, "right": False}
        frame_movement = (movement[0]+self.velocity[0],
                          movement[1] + self.velocity[1])

        # Checks the horizontal and vertical movement and collsions one by one
        self.pos[1] += frame_movement[1]
        if self.type in self.mob_types and self.game.player.recovering == 0:
            if self.check_player_collision("vertical"):
                vertical_collision_mob = True
        if self.type == "player" and self.game.player.recovering == 0:
            if self.check_mob_collision("vertical"):
                vertical_collision_player = True

        entety_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entety_rect.colliderect(rect) and self.can_colide:
                if frame_movement[1] > 0:
                    entety_rect.bottom = rect.top
                    self.collisions["down"] = True
                    if self.type == "player":
                        self.game.player.jump_count = 0
                if frame_movement[1] < 0:
                    entety_rect.top = rect.bottom
                    self.collisions["up"] = True

                    rect_pos = [(rect[0]/self.game.tilemap.tile_size),
                                (rect[1]/self.game.tilemap.tile_size)]

                    if rect_pos in self.game.tilemap.randoms and self.type == "player":
                        pos = str(int(rect_pos[0]))+";"+str(int(rect_pos[1]))
                        Randoms.all_randoms[pos].activate(pos)

                self.pos[1] = entety_rect.y

        self.pos[0] += frame_movement[0]
        if self.type in self.mob_types and vertical_collision_mob != True:
            self.check_player_collision("horisontal")
        if self.type == "player" and vertical_collision_player != True:
            self.check_mob_collision("horisontal")

        entety_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entety_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entety_rect.right = rect.left
                    self.collisions["right"] = True
                if frame_movement[0] < 0:
                    entety_rect.left = rect.right
                    self.collisions["left"] = True

                self.pos[0] = entety_rect.x

        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True

        if self.collisions["down"] or self.collisions["up"]:
            self.velocity[1] = 0
        elif self.can_colide:
            self.velocity[1] = min(5, self.velocity[1]+0.1)

        self.animation.update()

    def render(self, surf, offset=(0, 0)):
        """
        Renders the entity on the given surface, applying the specified offset.
        
        Args:
            surf (pygame.Surface): The surface to render the entity on.
            offset (tuple): The offset to apply to the entity's position.
        """
        # Render the entity on the given surface, applying offset for camera movement
        # Includes handling for the blinking effect during recovery
        if self.type == "player" and self.recovering > 9:
            if self.recovering == 0:
                adjustedR = self.rect()
                adjustedR.x = adjustedR.x - offset[0]
                adjustedR.y = adjustedR.y - offset[1]
                surf.blit(pg.transform.flip(self.animation.img(), self.flip, False), (
                    self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))
            else:
                adjustedR = self.rect()
                adjustedR.x = adjustedR.x - offset[0]
                adjustedR.y = adjustedR.y - offset[1]
                if self.recovering_blink < 10:
                    self.recovering_blink += 1
                    return
                if self.recovering_blink < 20:
                    surf.blit(pg.transform.flip(self.animation.img(), self.flip, False), (
                        self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))
                    self.recovering_blink += 1
                    return
                else:
                    self.recovering_blink = 0
        else:
            adjustedR = self.rect()
            adjustedR.x = adjustedR.x - offset[0]
            adjustedR.y = adjustedR.y - offset[1]
            surf.blit(pg.transform.flip(self.animation.img(), self.flip, False), (
                self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))


class Player(PhysicsEntity):
    """
    A specialized PhysicsEntity representing the player.
    
    Attributes:
        air_time (int): Counter for how long the player has been in the air.
        size_state (str): Indicates the player's size ('small' or 'big').
        recovering (int): Counter for the player's recovery time after being hit.
        jump_count (int): Counter for the number of consecutive jumps.
    """
    # Specialized PhysicsEntity representing the player
    def __init__(self, game, pos, size) -> None:
        """Initializes the Player with the game instance, position, and size."""
        # Initialize player-specific properties
        super().__init__(game, "player", pos, size)
        self.air_time = 0
        self.size_state = "small"
        self.recovering = 0
        self.jump_count = 0

    def update(self, tilemap, movement=(0, 0)):
        """
        Updates the player's state, including handling jumps, collisions, and animations.
        
        Args:
            tilemap (Tilemap): The game's tilemap for checking collisions.
            movement (tuple): The desired movement direction for the player.
        """
        # Update player state, including handling jumps and collisions
        super().update(tilemap, movement=movement)

        if self.recovering != 0:
            self.recovering -= 1
        self.air_time += 1

        if self.collisions["down"]:
            self.air_time = 0

            if movement[0] != 0:
                self.set_action(self.size_state + "/run")
            else:
                self.set_action(self.size_state + "/idle")

        if self.air_time > 4:
            self.set_action(self.size_state + "/jump")

    def check_mob_collision(self, direction):
        """
        Checks for and handles collisions with mob entities.
        
        Args:
            direction (str): The direction of the collision to check ('vertical' or 'horizontal').
        """
        # Detect and handle collisions with mobs
        for mob in self.game.harmfull_mobs:
            my_rect, mob_rect = self.rect(), mob.rect()
            if my_rect.colliderect(mob_rect) == True and direction == "vertical":
                self.game.player.velocity[1] = -2
                self.game.player.recovering = 9

                if mob.type == "koopa":
                    mob.shell()
                elif mob.type == "shell":
                    mob.direction = 0
                else:
                    self.game.harmfull_mobs.remove(mob)
                    pg.mixer.Sound("sounds/kick.wav").play()

            elif my_rect.colliderect(mob_rect) == True and direction == "horisontal" and not self.game.player.recovering:
                if mob.type == "shell":
                    if not self.flip:
                        mob.direction = 1
                    elif self.flip:
                        mob.direction = -1

                else:
                    self.game.player.sizedown()
                    self.game.player.recovering = 100

                return

    def sizeup(self):
        """Handles the player growth effect after collecting a power-up."""
        # Handle player growth effect after eating a sizeup shroom
        pg.mixer.Sound("sounds/powerup.ogg").play()
        if self.size_state == "small":
            self.size_state = "big"
            self.size[1] = self.size[1]+self.size[1]

    def sizedown(self):
        """Handles the player shrinking effect or triggers defeat if already small."""
        # Handle player shrinking or defeat
        if self.size_state == "big":
            self.size_state = "small"
            self.size[1] = self.size[1]-0.5*self.size[1]

        elif self.size_state == "small":
            self.game.defeat()


class Sizeup(PhysicsEntity):
    # Represents power-up items that can change the player's size
    def __init__(self, game, pos, size, direction="random") -> None:
        # Initialize with random movement direction
        super().__init__(game, "sizeup", pos, size)
        self.pos = [int(pos.split(";")[0])*self.game.tilemap.tile_size,
                    int(pos.split(";")[1])*self.game.tilemap.tile_size]
        self.start_pos = self.pos.copy()
        self.direction = direction
        self.velocity[1] = -0.4
        self.can_colide = False

        def generateID():
            while True:
                new_id = rd.randint(1, 10000)
                if not any(mob.id == new_id for mob in self.game.harmless_mobs):
                    return new_id
        self.id = generateID()

        if self.direction == "random":
            if rd.randint(0, 1) == 0:
                self.direction = -1
            else:
                self.direction = 1

    def update(self, tilemap, movement=(0, 0)):
        # Update state, handling movement and collisions
        super().update(tilemap, movement)
        if self.pos[1] > self.start_pos[1]-self.game.tilemap.tile_size and not self.can_colide:
            pass
        else:
            self.can_colide = True
            self.velocity[0] = self.direction*0.5

            if self.collisions["right"]:
                self.direction = -1
            if self.collisions["left"]:
                self.direction = 1
        if self.rect().colliderect(self.game.player.rect()) and self.game.player.size_state == "small":
            self.game.player.sizeup()
            for mob in self.game.harmless_mobs:
                if mob.id == self.id:
                    self.game.harmless_mobs.remove(mob)
        elif self.rect().colliderect(self.game.player.rect()):
            for mob in self.game.harmless_mobs:
                if mob.id == self.id:
                    self.game.harmless_mobs.remove(mob)


class Goomba(PhysicsEntity):
    """Follows same pattern as player."""
    # Represents Goomba enemies
    def __init__(self, game, pos, size) -> None:
        # Randomly assign initial movement direction
        super().__init__(game, "goomba", pos, size)

        def generateID():
            while True:
                new_id = rd.randint(1, 10000)
                if not any(mob.id == new_id for mob in self.game.harmfull_mobs):
                    return new_id
        self.id = generateID()
        self.game.harmfull_mobs.append(self)
        self.action = "run"

        self.pos = list(pos)
        self.size = list(size)
        self.direction = "random"

        if self.direction == "random":
            if rd.randint(0, 1) == 0:
                self.direction = -1
            else:
                self.direction = 1

    def update(self, tilemap, movement=(0, 0)):
        # Update Goomba state, handling movement and player collisions
        super().update(tilemap, movement=movement)

        self.velocity[0] = self.direction*0.3

        if self.collisions["right"]:
            self.direction = -1
        if self.collisions["left"]:
            self.direction = 1

        if rd.randint(0, 200) == 69:
            self.velocity[1] = -1.2

    def check_player_collision(self, direction):
        my_rect, player_rect = self.rect(), self.game.player.rect()
        if my_rect.colliderect(player_rect) == True and direction == "vertical":
            self.game.player.velocity[1] = -2
            self.game.player.recovering = 9
            for mob in self.game.harmfull_mobs:
                if mob.id == self.id:
                    self.game.harmfull_mobs.remove(mob)
                    pg.mixer.Sound("sounds/kick.wav").play()

                elif my_rect.colliderect(player_rect) == True and direction == "horisontal" and not self.game.player.recovering:
                    self.game.player.sizedown()
                    self.game.player.recovering = 100


class Koopa(PhysicsEntity):
    """Follows same pattern as player."""
    # Represents Koopa enemies, with unique behavior for turning into a shell
    def __init__(self, game, pos, size) -> None:
        super().__init__(game, "koopa", pos, size)

        def generateID():
            while True:
                new_id = rd.randint(1, 10000)
                if not any(mob.id == new_id for mob in self.game.harmfull_mobs):
                    return new_id
        self.id = generateID()
        self.game.harmfull_mobs.append(self)
        self.action = "run"

        self.pos = list(pos)
        self.size = list(size)
        self.direction = "random"

        if self.direction == "random":
            if rd.randint(0, 1) == 0:
                self.direction = -1
            else:
                self.direction = 1

    def update(self, tilemap, movement=(0, 0)):
        # Update Koopa state, handling movement and player collisions
        super().update(tilemap, movement=movement)

        self.velocity[0] = self.direction*0.3

        if self.collisions["right"]:
            self.direction = -1
            self.flip = True
        if self.collisions["left"]:
            self.direction = 1
            self.flip = False

        if rd.randint(0, 200) == 69:
            self.velocity[1] = -1.2

    def check_player_collision(self, direction):
        my_rect, player_rect = self.rect(), self.game.player.rect()
        if my_rect.colliderect(player_rect) == True and direction == "vertical":
            self.game.player.velocity[1] = -2
            self.game.recovering = 9
            for mob in self.game.harmfull_mobs:
                if mob.id == self.id:
                    self.shell()
        elif my_rect.colliderect(player_rect) == True and direction == "horisontal" and not self.game.player.recovering:
            self.game.player.sizedown()
            self.game.player.recovering = 100

    def shell(self):
        # Transform Koopa into a shell
        Shell(self.game, (self.pos[0], self.pos[1]+5), (10, 10))
        for mob in self.game.harmfull_mobs:
            if mob.id == self.id:
                self.game.harmfull_mobs.remove(mob)
                pg.mixer.Sound("sounds/kick.wav").play()


class Shell(PhysicsEntity):
    """Follows same pattern as player."""
    # Represents Koopa shells, which can move and cause damage
    def __init__(self, game, pos, size) -> None:
        super().__init__(game, "shell", pos, size)

        def generateID():
            while True:
                new_id = rd.randint(1, 10000)
                if not any(mob.id == new_id for mob in self.game.harmfull_mobs):
                    return new_id
        self.id = generateID()
        self.game.harmfull_mobs.append(self)
        self.direction = 0
        self.pos = list(pos)
        self.size = list(size)

    def update(self, tilemap, movement=(0, 0)):
        # Update shell state, handling movement and collisions
        super().update(tilemap, movement)
        if self.direction == 0:
            return

        self.velocity[0] = self.direction*3
        if self.collisions["right"]:
            self.direction = -1
        if self.collisions["left"]:
            self.direction = 1

    def check_player_collision(self, direction):
        # Detect and handle collisions with the player
        if self.direction != 0:
            my_rect, player_rect = self.rect(), self.game.player.rect()
            if my_rect.colliderect(player_rect) == True and direction == "vertical":
                self.game.player.velocity[1] = -2
                self.game.player.recovering = 9
                return

            elif my_rect.colliderect(player_rect) == True and direction == "horisontal" and not self.game.player.recovering:
                if self.direction == 0:
                    return
                else:
                    self.game.player.sizedown()
                    self.game.player.recovering = 100


class Randoms:
    """
    Represents a reward box object within the game, which can be activated to get rewards.

    These objects typically represent elements in the game world that, when interacted with, can yield power-ups, coins, or other items to the player. Activation of these objects changes their state to indicate that they have been used and potentially spawn items or effects.

    Attributes:
        game (Game): The game instance this random object belongs to.
        pos (str): The position of the random object within the tilemap, represented as a string in the format 'x;y'.
        activ (bool): Indicates whether the random object has been activated.
        reward (str): The type of reward that the random object yields upon activation. Defaults to 'random' indicating that the reward can vary.
    """

    all_randoms = {}
    """Class-level dictionary tracking all random objects by their positions."""

    def __init__(self, game, pos, reward="random"):
        """
        Initializes a new random interactive object with a specified position and reward.
        
        Args:
            game (Game): The game instance this object belongs to.
            pos (str): The position of the object within the tilemap, in 'x;y' format.
            reward (str, optional): The type of reward to yield. Defaults to 'random'.
        """
        self.game = game
        self.pos = pos
        self.activ = False
        self.reward = reward

        # Register the new object in the all_randoms dictionary
        Randoms.all_randoms[self.pos] = self

    def activate(self, pos):
        """
        Activates the random object, triggering its reward and marking it as used.

        This method changes the object's state to indicate that it has been activated. Depending on the implementation, this might involve changing the object's appearance in the game world, spawning items or effects, and potentially altering the game's tilemap.

        Args:
            pos (str): The position of the object being activated, in 'x;y' format.
        """
        if not self.activ:
            # Example: spawn a size-up power-up
            self.game.harmless_mobs.append(Sizeup(self.game, pos, (14, 14)))
            # Change the object's image to indicate it's been activated
            self.img = self.game.assets["random2"]
            self.activ = True

            # Update the tilemap to reflect the change in object type
            for key in self.game.tilemap.tilemap:
                if key == self.pos:
                    self.game.tilemap.tilemap[key]["type"] = "random2"
