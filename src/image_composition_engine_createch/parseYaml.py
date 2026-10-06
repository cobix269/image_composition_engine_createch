import yaml  ## Need uv add pyyaml
from pprint import pprint

def read_yaml():
    with open("conf.yml") as f:
        config = yaml.load(f, yaml.CFullLoader)
    pprint(config)
    print("*************")
    for layer in config["layers"]:
        print(layer["image"])
        print(layer["filters"])
        try:
            print(layer["blend"])
            print(layer["opacity"])
        except:
            print("")
        print("-----")
        # load image
        # apply filter
        # save img

read_yaml()