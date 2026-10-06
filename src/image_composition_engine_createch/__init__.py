from "./classes.py" import 
import yaml  ## Need uv add pyyaml
from pprint import pprint

def main():
    with open("conf.yml") as f:
        config = yaml.load(f, yaml.CFullLoader)
    pprint(config)
    print("*************")
    for layer in config["layers"]:
        print(layer["image"])
        print(layer["filters"])
        print("-----")
        # load image
        # apply filter
        # save img

main()