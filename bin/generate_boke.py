# -*- coding: utf-8 -*-
import argparse
from img2seq import GenerateBoke
from img2seq import DataProcessor
from img2seq import Resource


def main():
    parser = argparse.ArgumentParser(description="Bokete Model")
    parser.add_argument('-c', '--config', required=True,
                        type=str, help='path to configuration file')
    parser.add_argument('-m', '--model', required=True,
                        type=str, help='Bokete model file')
    args = parser.parse_args()
    config = Resource(args.config, train=False).config
    model_path = args.model

    gen = GenerateBoke(model_path, config)
    gen.load_vocabulary()
    gen.setup_model()

    data = DataProcessor(config)
    data.prepare()

    for boke, image in data.batch_iter(batchsize=1, kind="dev"):
        print gen.generate_from_array(image)


if __name__ == '__main__':
    main()
