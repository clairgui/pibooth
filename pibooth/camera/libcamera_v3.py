# -*- coding: utf-8 -*-

import pygame
try:
    import picamera2
    from picamera2 import Picamera2
    from libcamera import Transform
    import numpy
except ImportError:
    picamera2 = None  # picamera2 is optional
from PIL import ImageFilter
from pibooth.pictures import sizing
from pibooth.utils import LOGGER
from pibooth.camera.base import BaseCamera
from pibooth.tasks import AsyncTask
from pibooth import evts
import time


def get_libcamera_camera_proxy(port=None):
    """Return camera proxy if a Raspberry Pi compatible camera is found
    else return None.

    :param port: look on given index number
    :type port: int
    """
    if not picamera2:
        return None  # picamera2 is not installed

    cameras = Picamera2.global_camera_info()
    if cameras:
        LOGGER.debug("Found libcamera cameras:")
        for index, info in enumerate(cameras):
            selected = ">" if index == port or (port is None and index == 0) else "*"
            LOGGER.debug("  %s %s : name-> %s | addr-> %s", selected, f"{index:02d}", info["Model"], info["Location"])

        if port is not None:
            return Picamera2(camera_num=port)
        return Picamera2()

    return None


class LibCamera(BaseCamera):

    """Libcamera camera management.
    """

    def __init__(self, libcamera_camera_proxy):
        super().__init__(libcamera_camera_proxy)
        # self._preview_config = self._cam.create_preview_configuration(raw=self._cam.sensor_modes[1], display='raw')
        self._preview_config = self._cam.create_preview_configuration()
        # self._preview_config = self._cam.create_still_configuration()
        self._capture_config = self._cam.create_still_configuration()

    def _specific_initialization(self):
        """Camera initialization.
        """
        self._cam.stop()

        # utilisation de la transformation par défaut
        self._preview_config['transform'] = Transform(hflip=True)
        # un buffer de 6 permet moins de latence lors de la preview
        self._preview_config['buffer_count'] = 3
        # Queue = false pour la preview 
        self._preview_config['queue'] = True
        # Format from lore YUV420 not supported by PIL image
        self._preview_config['format'] = 'RGB888'

        h = 300
        l = round(h*1.777) # 1920
        if(l%2 > 0):
            # size should be even numbers 
            l = l + 1 
        self._preview_config['main']['size'] = (l,h)
        self._cam.align_configuration(self._preview_config)

        # améliore la qualité de l'image
        self._cam.options["quality"] = 95 
        self._cam.options["compress_level"] = 0
        self._cam.configure(self._preview_config)

        self._cam.configure(self._capture_config)
        self._cam.start()

    def _show_overlay(self):
        """Add an image as an overlay.
        """
        self._overlay = self._build_overlay(self._preview_config['main']['size'], self._overlay_text, self._overlay_alpha)
        # self._cam.set_overlay(numpy.array(self._overlay))
        # LOGGER.debug("overlay text '%s'" , self._overlay_text)

    def _hide_overlay(self):
        """Remove any existing overlay.
        """
        if self._overlay:
            self._cam.set_overlay(None)
            self._overlay = None
            self._overlay_text = None

    def _process_capture(self, capture_data):
        """Rework capture data.

        :param capture_data: couple (PIL Image, effect)
        :type capture_data: tuple
        """
        image, effect = capture_data
        if effect != 'none':
            image = image.filter(getattr(ImageFilter, effect.upper()))
        
        # Cropping
        width, height = image.size
        left = 800
        top = 400
        right = width - 800
        bottom = height - 400
        image = image.crop((left, top, right, bottom))
        return image

    def get_preview_image(self):
        """Capture a new picture in a file.
        """
        image = self._cam.capture_image('main')
        if self._overlay is not None:
            image.paste(self._overlay, (0, 0), self._overlay)
        return image

    def preview(self, rect, flip=True):
        """Display a preview on the given Rect (flip if necessary).
        """
        LOGGER.debug("In preview in libcamera")
        # Define Rect() object for resizing preview captures to fit to the defined
        # preview rect keeping same aspect ratio than camera resolution.
        # size = sizing.new_size_keep_aspect_ratio(
        #     self.resolution, 
        #     (min(rect.width, self._cam.sensor_resolution[0]), 
        #      min(rect.height, self._cam.sensor_resolution[1])))
        # size = sizing.new_size_keep_aspect_ratio(
        #     self.resolution, 
        #     (float(self._cam.sensor_resolution[0]), 
        #     float(self._cam.sensor_resolution[1])))
        # rect = pygame.Rect(rect.centerx - size[0] // 2, rect.centery - size[1] // 2,
        #                    size[0], size[1],)
        LOGGER.debug("Resolution '%d', '%d'",self.resolution[0], self.resolution[1])
        LOGGER.debug("rectg '%d', '%d'",
                     rect.size[0], 
                    rect.size[1])
        # size = sizing.new_size_keep_aspect_ratio(self.resolution, (rect.width, rect.height))
        # rect = pygame.Rect(rect.centerx - size[0] // 2, rect.centery - size[1] // 2, size[0], size[1])


        # self._preview_config['main']['size'] = rect.size # prend du temps
        # # self._preview_config['main']['size'] = (self._cam.sensor_resolution[0]//2,self._cam.sensor_resolution[0]//2) # prend du temps
        # # self._preview_config['transform'] = Transform()
        self._cam.switch_mode(self._preview_config)
        # self._cam.switch_mode(self._capture_config) # fonctionne mais est lent
        # image complète mais ne rempli pas tout le rectangle => Modifier la taille du rectangle pour la preview
        super().preview(rect, flip)


    def get_capture_image(self, effect=None):
        """Capture a new picture in a file.
        """
        self._cam.switch_mode(self._capture_config)
        image = self._cam.capture_image('main')
        self._captures.append((image, effect))
        return image

    def _specific_cleanup(self):
        """Close the camera driver, it's definitive.
        """
        self._cam.stop()
