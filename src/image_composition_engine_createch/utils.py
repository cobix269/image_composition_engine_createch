from PIL import Image
import numpy as np
from dataclasses import dataclass
import scipy.ndimage
from classes.py import Layer

def img2RGB(src: str) -> np.ndarray:
    img: Image = Image.open(src)
    return np.array(img.convert('RGB'))

def array_from_file(path : str) -> np.ndarray:
    image = Image.open(path).convert('RGB')
    im = np.array(image) / 255
    return im
def array_to_image(arr : np.ndarray) :
    adjusted = np.array(np.clip(arr , 0, 1) * 255, dtype=np.uint8)
    new_pil_im = Image.fromarray(adjusted)   
    return new_pil_im
def show_from_array(arr : np.ndarray) :
    img = array_to_image(arr)
    img.show() 
def display_from_array(arr : np.ndarray) :
    img = array_to_image(arr)
    display(img)
    
#pour les images RGBA 
def array_from_file_RGBA(path : str) -> np.ndarray:
    image = Image.open(path).convert('RGBA')
    im = np.array(image) / 255
    return im
def array_to_image_RGBA(arr : np.ndarray) :
    adjusted = np.array(np.clip(arr , 0, 1) * 255, dtype=np.uint8)
    new_pil_im = Image.fromarray(adjusted)   
    return new_pil_im
def show_from_array_RGBA(arr : np.ndarray) :
    img = array_to_image_RGBA(arr)
    img.show()
def display_from_array_RGBA(arr : np.ndarray) :
    img = array_to_image_RGBA(arr)
    display(img)


def compose(layers: list[Layer]) -> np.ndarray:
    """Superpose des calques RGB ou RGBA sur un fond noir."""
    if not layers:
        raise ValueError("Il faut au moins un calque.")

    height, width = layers[0].pixels.shape[:2]
    out = np.zeros((height, width, 3), dtype=np.float32)

    for layer in layers:
        pixels = layer.pixels

        if pixels.ndim != 3 or pixels.shape[2] not in (3, 4):
            raise ValueError("Chaque calque doit être RGB ou RGBA.")
        if pixels.shape[:2] != (height, width):
            raise ValueError("Les calques doivent avoir les mêmes dimensions.")
        if not 0 <= layer.opacity <= 1:
            raise ValueError("L'opacité doit être comprise entre 0 et 1.")

        src = pixels[:, :, :3].astype(np.float32)
        alpha = layer.opacity

        if pixels.shape[2] == 4:
            alpha = alpha * pixels[:, :, 3:4].astype(np.float32) / 255

        out = (1 - alpha) * out + alpha * src

    return np.clip(np.rint(out), 0, 255).astype(np.uint8)
