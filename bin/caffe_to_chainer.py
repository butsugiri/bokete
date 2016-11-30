# -*- coding: utf-8 -*-
import cPickle as pickle
from chainer.links.caffe import CaffeFunction

vgg = CaffeFunction('../caffenet.caffemodel')
with open("./caffenet.pkl", 'wb') as fo:
    pickle.dump(vgg, fo)
