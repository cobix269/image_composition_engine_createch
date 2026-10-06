from PIL import Image
import numpy as np
from dataclasses import dataclass
import scipy.ndimage

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
