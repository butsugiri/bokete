# -*- coding: utf-8 -*-
import sys
import json
import os
from datetime import datetime
from pprint import pformat
from utils import log_api as LogAPI


class Resource(object):
    def __init__(self, config_path, train=True):
        time = datetime.now().strftime('%Y%m%d_%H_%M_%S')
        self.logger = LogAPI.create_logger(self.__class__.__name__, debug=True)

        with open(config_path, "r") as fi:
            self.config = json.load(fi)
        self.logger.info("*** Hyper Prameters ***")
        self.logger.info(pformat(self.config) + "\n")

        self.config["train_data"] = os.path.join(self.config["data_root"], self.config["data_name"], "train.json.parsed")
        self.config["dev_data"] = os.path.join(self.config["data_root"], self.config["data_name"], "dev.json.parsed")

        self.config["vocab_path"] = os.path.join(self.config["data_root"], self.config["data_name"], "vocab.txt")
        if self.config["local_run"]:
            self.config["image_path"] = os.path.join(self.config["data_root"], "images")
        else:
            self.config["image_path"] = os.path.join("../../../bokete/data/", "images")
        self.config["time"] = time

        if train:
            os.mkdir("../result/" + time)
            self.config["log_path"] = "../result/" + time + "/stats.json"
            self.config["est_path"] = "../result/" + time + "/estimates.json"
            # snapshot用のディレクトリを準備
            os.mkdir("../result/" + time + "/model_files/")
            self.config["model_path"] = "../result/" + time + "/model_files/"
