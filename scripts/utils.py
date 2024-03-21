import pygame as pg
import os

BASE_IMG_PATH = "images/" # Path to folder containing all images

def load_image(path, colorkey=(0, 0, 0)):
    """
    Loads a single image from a specified path, applying a color key for transparency.
    
    Args:
        path (str): The path to the image relative to the base image path.
        colorkey (tuple): The RGB value of the color to be treated as transparent.
    
    Returns:
        pygame.Surface: The loaded image with the colorkey applied.
    """
    img = pg.image.load(BASE_IMG_PATH + path).convert()
    img.set_colorkey(colorkey)
    return img

def load_images(path, colorkey=(0, 0, 0)):
    """
    Loads all images from a specified directory, applying the same color key for transparency to each.
    
    Args:
        path (str): The directory path relative to the base image path containing the images to load.
        colorkey (tuple): The RGB value of the color to be treated as transparent for all images.
    
    Returns:
        list: A list of pygame.Surface objects representing the loaded images.
    """
    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        images.append(load_image(path + '/' + img_name, colorkey))
    return images

class Animation:
    """
    Represents an animation sequence composed of multiple images.
    
    Attributes:
        images (list): A list of pygame.Surface objects representing the animation frames.
        img_duration (int): The duration each frame is displayed for.
        loop (bool): Whether the animation should loop.
        done (bool): Whether the animation has completed (relevant for non-looping animations).
        frame (int): The current frame index of the animation.
    """
    
    def __init__(self, images, img_dur=5, loop=True):
        """
        Initializes a new Animation instance.
        
        Args:
            images (list): A list of pygame.Surface objects for the animation frames.
            img_dur (int): The duration each frame is displayed for.
            loop (bool): Whether the animation should loop.
        """
        self.images = images
        self.loop = loop
        self.img_duration = img_dur
        self.done = False
        self.frame = 0

    def copy(self):
        """
        Creates a copy of the animation.
        
        Returns:
            Animation: A new Animation instance with the same images, duration, and loop setting.
        """
        return Animation(self.images, self.img_duration, self.loop)

    def update(self):
        """
        Updates the animation frame, advancing the animation or marking it as done if not looping.
        """
        if self.loop:
            self.frame = (
                self.frame + 1) % (self.img_duration * len(self.images))
        else:
            self.frame = min(
                self.frame + 1, self.img_duration * len(self.images) - 1)
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True

    def img(self):
        """
        Gets the current frame of the animation.
        
        Returns:
            pygame.Surface: The current frame's image.
        """
        return self.images[int(self.frame / self.img_duration)]
