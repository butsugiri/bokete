# -*- coding: utf-8 -*-
import sys
import MeCab
import json

"""
items.jsonを標準入力から受け取って
形態素解析した結果を格納するスクリプト
"""


def parse_json(fi):
    mt = MeCab.Tagger("mecabrc")
    for line in fi:
        data = json.loads(line)

        res = mt.parse(data["boke"].encode("utf-8")).split("\n")
        raw_surs = [x.split("\t")[0] for x in res if x != "EOS" and x != ""]
        surs = [x for x in raw_surs if x != "　"]
        surs.insert(0, u"<BOS>")
        surs.append(u"<EOS>")

        data["parsed"] = surs
        sys.stdout.write(json.dumps(data, ensure_ascii=False) + "\n")


if __name__ == '__main__':
    parse_json(sys.stdin)
