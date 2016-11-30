# -*- coding: utf-8 -*-
import sys
import chainer
import chainer.links as L
import chainer.functions as F
import chainer.serializers as S
from chainer import cuda
from DataProcessor import ImageProcessor
from Model import Img2Seq
import numpy as np


class GenerateBoke(object):
    def __init__(self, model_path, config):
        self.config = config
        self.model_path = model_path
        self.vocab_path = config["vocab_path"]
        self.model = None
        self.vocab = None
        # 最長の出力とは
        self.max_length = 50  # これこそヒューリスティック
        self.n_unit = self.config["embed_dim"]

    def load_vocabulary(self):
        with open(self.vocab_path) as fi:
            self.vocab = {unicode(x.split()[0]): int(x.split()[1]) for x in fi}
        self.ivocab = {v: k for k, v in self.vocab.iteritems()}

    def setup_model(self):
        n_vocab = len(self.vocab)
        predictor = Img2Seq(n_vocab, self.config)
        self.model = L.Classifier(predictor)
        S.load_npz(self.model_path, self.model)

    def generate_from_array(self, img_array):
        img_array = np.asarray(img_array, dtype=np.float32)
        if len(img_array.shape) == 3:  # 3次元
            img_array = img_array.reshape((1,) + img_array.shape)
            return self.generate(img_array)
        elif len(img_array.shape) == 4:
            if img_array.shape[0] != 1:
                sys.stderr.write("wrong dimension\n")
                raise Exception
            else:
                return self.generate(img_array)
        else:
            sys.stderr.write("wrong dimension\n")
            raise Exception

    def generate_from_path(self, img_path):
        img_array = self._preprocess_image(img_path)
        img_array = img_array.reshape((1,) + img_array.shape)
        return self.generate(img_array)

    def generate(self, img_array, primetext=u"<BOS>"):
        """
        input must be 4-dimensional array with first dimension == 1
        """
        img_vec = self.model.predictor.encode_image(img_array)
        # self.model.predictor.set_image(img_vec)
        self.model.predictor.reset_state()
        cell, hidden = self.model.predictor.get_state()

        initial_state = {
            "path": [primetext],
            "cell": chainer.Variable(np.zeros((1, self.config["embed_dim"])).astype(np.float32)),
            "hidden": chainer.Variable(np.zeros((1, self.config["hidden_dim"])).astype(np.float32)),
            "prob": 0,
            "begin": True
        }
        candidates = [initial_state]

        length = 0
        width = 3
        while length < self.max_length:
            temp = [x for x in candidates if x["path"][-1] == u"<EOS>"]
            yet_to_gen = [x for x in candidates if x["path"][-1] != u"<EOS>"]
            for candidate in yet_to_gen:
                self.model.predictor.set_state(candidate["cell"], candidate["hidden"])
                prev_word = np.asarray([self.vocab[candidate["path"][-1]]], dtype=np.int32)

                if candidate["begin"]:
                    probs = F.softmax(self.model.predictor(prev_word, img_vec))
                    candidate["begin"] = False
                else:
                    probs = F.softmax(self.model.predictor(prev_word))
                candidates = probs.data[0].argsort()[-1 * width:][::-1]
                cell, hidden = self.model.predictor.get_state()

                for idx in candidates:
                    token = self.ivocab[idx]
                    state = {
                        "path": [x for x in candidate["path"]] + [token],
                        "cell": cell,
                        "hidden": hidden,
                        "prob": candidate["prob"] + np.log(probs.data[0][idx]),
                        "begin": False
                    }
                    temp.append(state)

            candidates = sorted(temp, key=lambda x: x["prob"], reverse=True)[:width]
            if len([x for x in candidates if x["path"][-1] == u"<EOS>"]) == width:
                break
            length += 1
        print temp
        return " ".join(sorted(temp, key=lambda x: x["prob"], reverse=True)[0]["path"][0:-1])

        # prev_word = np.asarray([self.vocab[primetext]], dtype=np.int32)
        #
        # sentence = []
        # for i in xrange(self.max_length):
        #     prob = F.softmax(self.model.predictor(prev_word))
        #     probability = cuda.to_cpu(prob.data)[0].astype(np.float64)
        #     probability /= np.sum(probability)
        #     index = np.random.choice(range(len(probability)), p=probability)
        #     if self.ivocab[index] == u'<EOS>':
        #         sentence.append("。")
        #         break
        #     else:
        #         sentence.append(self.ivocab[index])
        #
        #     prev_word = chainer.Variable(np.array([index], dtype=np.int32))
        # self.model.predictor.reset_state()
        # return " ".join(sentence)




    def _preprocess_image(self, img_path):
        return ImageProcessor(img_path).prepare()
