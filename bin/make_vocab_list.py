# -*- coding: utf-8 -*-
"""
parseしたjsonを受け取り，各単語をID化するスクリプト
引数でしきい値を指定し，登場頻度がそれ以下の単語はすべてUNKに置き換える．
"""

import sys
import argparse
import json
from collections import defaultdict


def main(fi, threshold):
    passage_freqs = defaultdict(int)
    for line in fi:
        data = json.loads(line.rstrip())
        for token in data["parsed"]:
            if token.strip() != "":
                passage_freqs[token] += 1

    passage_ids = defaultdict(lambda: len(passage_ids))
    passage_ids[u"<UNK>"]
    passage_ids[u"<BOS>"]
    passage_ids[u"<EOS>"]
    for vocab, freq in passage_freqs.iteritems():
        if freq <= threshold:
            continue
        else:
            passage_ids[unicode(vocab)]

    for vocab, _id in passage_ids.iteritems():
        sys.stdout.write("{}\t{}\n".format(vocab, _id))

    sys.stderr.write("Threshold Value: {}\nOriginal Vocab Size:{}\tVocab Size (After Cut-off):{}\n".format(
        threshold,
        len(passage_freqs),
        len(passage_ids),
    ))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vocab creator")
    parser.add_argument('-t', '--threshold', dest='threshold',
                        default=2, type=int, help='しきい値')
    args = parser.parse_args()
    main(sys.stdin, args.threshold)
