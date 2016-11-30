# -*- coding: utf-8 -*-
import sys
import chainer
import chainer.links as L
import cPickle as pickle
import numpy as np


class Img2Seq(chainer.Chain):

    def __init__(self, n_vocab, config):
        self.config = config
        self.embed_dim = config["embed_dim"]
        self.hidden_dim = config["hidden_dim"]
        self.n_vocab = n_vocab

        if config["use_caffenet"]:
            with open(self.config["caffemodel_path"], "rb") as caffemodel:
                sys.stderr.write("Loading Caffemodel...")
                enc_img = pickle.load(caffemodel)
                sys.stderr.write("done.\n")
        else:
            enc_img = L.Linear(1, 1)

        super(Img2Seq, self).__init__(
            embed_mat=L.EmbedID(n_vocab, self.embed_dim, ignore_label=-1),
            dec_lstm=L.LSTM(self.embed_dim, self.hidden_dim),
            l1=L.Linear(self.hidden_dim, n_vocab),
            img2x=L.Linear(4096, self.embed_dim),
            enc_img=enc_img
        )

    def __call__(self, x, img_vec=None):
        if img_vec is not None:
            h0 = self.embed_mat(x) + img_vec
        else:
            h0 = self.embed_mat(x)
        h1 = self.dec_lstm(h0)
        y = self.l1(h1)
        return y

    def encode_image(self, img_array):
        batchsize = img_array.shape[0]
        if self.config["use_caffenet"]:
            img_x = chainer.Variable(img_array, volatile='on')
            y = self.enc_img(
                inputs={"data": img_x},
                outputs={"fc7"})[0]
        else:
            x = self.xp.random.rand(batchsize, 4096).astype(np.float32)
            y = chainer.Variable(x)
        y.volatile = 'off'
        return self.img2x(y)

    def reset_state(self):
        self.dec_lstm.reset_state()

    def set_state(self, c, h):
        self.dec_lstm.set_state(c, h)

    def get_state(self):
        return (self.dec_lstm.c, self.dec_lstm.h)


if __name__ == '__main__':
    from Resource import Resource

    resource = Resource("../../config/toy.json")
    with open("../../data/toy/vocab.txt") as fi:
        n_vocab = sum(1 for x in fi)
    Img2Seq(n_vocab, resource.config)
