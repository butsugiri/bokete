# -*- coding: utf-8 -*-
import json
import chainer
import chainer.links as L
import chainer.serializers as S
import numpy as np
import utils.log_api as LogAPI
from datetime import datetime
from DataProcessor import DataProcessor
from Model import Img2Seq
from chainer import cuda

"""
train: 学習データ、または作成済みDataProcessorを受け取り、学習の実行(set_optimizerで作成したoptimizerのupdate)を行う。
この過程で、進捗状況を定期的にreportする。
"""


class Trainer(object):

    def __init__(self, config, debug=True):
        self.config = config
        self.debug = debug
        self.logger = LogAPI.create_logger(self.__class__.__name__, self.debug)

        self.data_processor = DataProcessor(config)
        self.data_processor.prepare()
        n_vocab = len(self.data_processor.vocab)
        self.model = L.Classifier(Img2Seq(n_vocab, config))
        self.model.compute_accuracy = False  # I want loss, not accuracy
        self.optimizer = chainer.optimizers.Adam()
        self.optimizer.setup(self.model)

        if self.config['use_gpu'] >= 0:
            chainer.cuda.get_device(self.config['use_gpu']).use()
            self.model.to_gpu()
            self.xp = cuda.cupy
        else:
            self.xp = np

        # パラメータ・実験結果を保存しておくdict
        self.result_storage = {}
        self.result_storage["result"] = {
            "total_loss": [], "average_loss": [], "time_taken": [], "hyper_params": config}

    def _calc_loss(self, batch):
        boke, img = batch
        boke = self.xp.asarray(boke, dtype=np.int32)
        img = self.xp.asarray(img, dtype=np.float32)

        # 1. ベクトル化してある画像をCNNに入れて特徴ベクトルにする
        img_vec = self.model.predictor.encode_image(img)
        # この時点で画像は入力(word embedding)と同じ次元
        # もしかして: これLinkの外に出したほうがいいか？

        # 3. bokeをデコードするように学習
        accum_loss = 0
        n = 0
        for curr_words, next_words in zip(boke.T, boke[:, 1:].T):
            if n == 0:
                accum_loss += self.model(curr_words, img_vec, next_words)
            else:
                accum_loss += self.model(curr_words, next_words)
            n += 1
        return accum_loss

    def run(self):
        for epoch in xrange(self.config["total_epoch"]):
            self.logger.info("Currently at Epoch #{}".format(epoch + 1))
            self.epoch_start_time = datetime.now()

            for batch in self.data_processor.batch_iter():
                loss = self._calc_loss(batch)
                self.optimizer.target.zerograds()
                loss.backward()
                self.optimizer.update()

            self.epoch_end_time = datetime.now()
            if (epoch + 1) % 3 == 0:
                self._take_snapshot(epoch)
                self.evaluate(epoch)

    def evaluate(self, epoch):
        self.logger.info("Processing Validation...")
        accum_loss = 0
        n_samples = 0

        for batch in self.data_processor.batch_iter(kind="dev"):
            accum_loss += cuda.to_cpu(self._calc_loss(batch).data)
            n_samples += len(batch[0])  # batchsize

        # epoch単位の実行時間の計算
        td = self.epoch_end_time - self.epoch_start_time  # td: timedelta
        hours, remainder = divmod(td.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_taken = "{hours:02d}:{minutes:02d}".format(
            hours=hours, minutes=minutes)

        total_loss = float(accum_loss)
        average_loss = total_loss / n_samples
        self.logger.info("Epoch: #{epoch}\tTotal Loss:{total:.4f}\tAverage Loss:{average:.4f}\tTime Taken:{time_taken}\n".format(
            epoch=epoch,
            total=total_loss,
            average=average_loss,
            time_taken=time_taken
        ))

        # accuracy/total loss/average lossをそれぞれ格納
        self.result_storage["result"]["total_loss"].append(total_loss)
        self.result_storage["result"]["average_loss"].append(average_loss)
        self.result_storage["result"]["time_taken"].append(time_taken)
        # 格納したstatsをファイルに保存
        self._save_stats()

    def _take_snapshot(self, epoch):
        """
        訓練したモデルをepochごとに保存していくメソッド
        """
        path = "{}/{:02d}.npz".format(self.config["model_path"], epoch)
        S.save_npz(path, self.model)

    def _save_stats(self):
        """
        stats.json (accuracy/average loss/total lossを保存するjson) を
        epochごとに書き換えるメソッド
        """
        with open(self.config["log_path"], "w") as result:
            result.write(json.dumps(self.result_storage))
            result.flush()


if __name__ == '__main__':
    from Resource import Resource
    resource = Resource("../../config/toy.json")
    with open("../../data/toy/vocab.txt") as fi:
        n_vocab = sum(1 for x in fi)
    trainer = Trainer(resource.config)
    trainer.run()
