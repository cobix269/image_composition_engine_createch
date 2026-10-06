from parseYaml import read_yaml
from classes import Layer
from constants import R, G, B, A
from utils import show_from_array, compose
images = read_yaml()

layers = []

for image in images:
    layers.append(Layer(src=image,opacity=0.5))

img = compose(layers)
show_from_array(img)