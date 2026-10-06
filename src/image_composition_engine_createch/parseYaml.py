from logging import raiseExceptions
import yaml  ## Need uv add pyyaml
from pprint import pprint
from .utils import *

def read_yaml():
    with open("conf.yml") as f:
        config = yaml.load(f, yaml.CFullLoader)
    return config
    
def parse_yaml():
    data: dict = read_yaml()
    for layer in data["layers"]:
        for image in layer["image"]:
            try:
                array_from_file(image)
            except:
                raise ValueError(f"L'image {image} n'existe pas.")

        for filter in layer["filters"]:
            
    pprint(data)

parse_yaml()