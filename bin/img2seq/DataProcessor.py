# -*- coding: utf-8 -*-
import json
import os
import numpy as np
import utils.log_api as LogAPI
from PIL import Image
from collections import defaultdict
from Resource import Resource
from itertools import islice


class BoketeImage(object):

    def __init__(self, boke, parse, image_path, star, vocab):
        """
        本当はvocabも受け取ってidxに落とす
        """
        self.boke = boke
        self.parse = [vocab[unicode(x)] if unicode(x) in vocab else vocab[u"<UNK>"] for x in parse]
        self.image_path = image_path
        self.star = star

    def __str__(self):
        return "boke: {}\timage: {}\tstar: {}".format(self.boke, self.image_path, self.star)


class ImageProcessor(object):
    """
    heavily inspired by https://github.com/icoxfog417/mlimages/blob/master/mlimages/model.py
    """
    def __init__(self, path, width=227, height=227):
        self.path = path  # path to the image file
        self.image = None
        self.width = width
        self.height = height

    def load(self):
        self.image = Image.open(self.path)

    def prepare(self):
        self.load()
        self._downscale()
        return self._subtract_mean(self._to_array())

    def _downscale(self):
        if self.image.size[0] >= self.width and self.image.size[1] >= self.height:
            target_v_ratio = self.height / self.width
            actual_v_ratio = self.image.size[1] / self.image.size[0]

            if target_v_ratio != actual_v_ratio:
                if actual_v_ratio > 1:
                    # height > width
                    _w = self.image.size[0]
                    self.__crop_from_center(_w, int(target_v_ratio * _w))
                else:
                    # height < width
                    _h = self.image.size[1]
                    self.__crop_from_center(int(target_v_ratio * _h), _h)
                self.image.thumbnail((self.width, self.height))
            else:
                self.__crop_from_center(self.width, self.height)

    def __crop_from_center(self, width, height):
        im_width, im_height = self.image.size
        get_bound = lambda length, size: int((length - size) / 2)
        self.__crop_from_lefttop(get_bound(im_width, width), get_bound(im_height, height), width, height)

    def __crop_from_lefttop(self, left, top, width, height):
        self.image = self.image.crop((left, top, left + width, top + height))

    def _to_array(self, color=True):
        img = np.asarray(self.image, dtype=np.float32)
        if img.ndim == 2:
            img = img[:, :, np.newaxis]
            if color:
                img = np.tile(img, (1, 1, 3))
        elif img.shape[2] == 4:
            img = img[:, :, :3]

        # height * width * 深度 --> 深度 * height * width
        img = img.transpose(2, 0, 1)

        return img

    def _subtract_mean(self, img_array):
        mean_image = np.ndarray((3, 227, 227), dtype=np.float32)
        mean_image[0] = 103.939
        mean_image[1] = 116.779
        mean_image[2] = 123.68
        return img_array - mean_image


class DataProcessor(object):
    """docstring for DataProcessor."""

    def __init__(self, config, debug=True):
        self.config = config
        self.debug = debug

        # 画像のクロップ後サイズ
        self.width = 227
        self.height = 227

        self.logger = LogAPI.create_logger(
            self.__class__.__name__, self.debug)

    def prepare(self):
        self.logger.info("Loading Vocabulary...")
        with open(self.config["vocab_path"]) as fi:
            self.vocab = {unicode(x.split()[0]): int(x.split()[1]) for x in fi}
        self.logger.info("done.")

        # TODO: 訓練と評価データの切り分け
        self.logger.info("Loading Dataset...")
        self.train_data = self._load_dataset(kind="train")
        self.dev_data = self._load_dataset(kind="dev")
        self.logger.info("done.")

    def data_stats(self):
        """
        データセットの統計量を取得したい
        統計量の種類:
            ユニークな画像の枚数
            ボケの総数
            ボキャブラリの数
        """
        train_stats = self._get_data_stats(kind="train")
        dev_stats = self._get_data_stats(kind="dev")

        with open(self.config["vocab_path"]) as fi:
            n_vocab = len([x for x in fi])

        out = {
            "train": train_stats,
            "dev": dev_stats,
            "n_vocab": n_vocab,
            "data_name": self.config["data_name"]
        }
        return out

    def _get_data_stats(self, kind="train"):
        if kind == "train":
            dataset = self.config["train_data"]
        elif kind == "dev":
            dataset = self.config["dev_data"]
        unique_images = set()
        line_count = 0
        with open(dataset) as fi:
            for line in fi:
                line = json.loads(line)
                unique_images.add(line["images"][0]["url"])
                line_count += 1
        out = {
            "total_boke": line_count,
            "unique_images": len(list(unique_images))
        }
        return out

    def _load_dataset(self, kind):
        if kind == "train":
            path = self.config["train_data"]
        elif kind == "dev":
            path = self.config["dev_data"]

        dataset = []
        with open(path) as fi:
            for line in fi:
                data = json.loads(line)
                img_basename = data["images"][0]["path"]
                bokete_image = BoketeImage(
                    boke=unicode(data["boke"]),
                    parse=data["parsed"],
                    image_path=os.path.join(self.config["image_path"], img_basename),
                    star=data["star"],
                    vocab=self.vocab
                )
                dataset.append(bokete_image)
        return dataset

    def batch_iter(self, batchsize=8, kind="train"):
        """
        dataset(リスト)をミニバッチサイズに刻んで出力
        やること: 画像の前処理，読み込みなどなど
        """
        if kind == "train":
            dataset = self.train_data
        elif kind == "dev":
            dataset = self.dev_data
        same_length = defaultdict(list)

        for data in dataset:
            same_length[len(data.parse)].append(data)

        for datas in same_length.itervalues():
            N = len(datas)
            for i in xrange(0, N, batchsize):
                yield [x.parse for x in datas[i:i + batchsize]], [ImageProcessor(x.image_path).prepare() for x in datas[i:i + batchsize]]


if __name__ == '__main__':
    resource = Resource("../../config/toy.json")
    data = DataProcessor(resource.config)
    data.prepare()
    for x, y in data.batch_iter():
        print x[0]
