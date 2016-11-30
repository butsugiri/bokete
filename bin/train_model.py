# -*- coding: utf-8 -*-
import argparse
from img2seq import Trainer
from img2seq import Resource


def main():
    parser = argparse.ArgumentParser(description="BokeBoke")
    parser.add_argument('-c', '--config', dest='config',
                        default="../config/toy.json", type=str, help='path to configuration file')
    args = parser.parse_args()
    config = Resource(args.config).config
    trainer = Trainer(config)
    trainer.run()

if __name__ == '__main__':
    main()
