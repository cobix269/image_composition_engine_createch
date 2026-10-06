from PIL import Image
import numpy as np
from dataclasses import dataclass
import scipy.ndimage

def img2RGB(src: str) -> np.ndarray:
    img: Image = Image.open(src)
    return np.array(img.convert('RGB'))