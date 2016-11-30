#!/bin/sh

# 必要な前処理を全部します
# vocab.txtとitems.json.parsedの作成を目指す
# 元々のimgファイルを細かく切り分けるのは別のスクリプトに任す．
# /"hogehoge"/train/ and /dev/ができていると仮定

if [ $# -ne 1 ]; then
  echo "指定された引数は$#個です。" 1>&2
  echo "実行するには1個の引数が必要です。" 1>&2
  exit 1
fi


NAME=$1
python ./parse_items2json.py < "../data/$NAME/train.json" > "../data/$NAME/train.json.parsed"
echo "parsed training data" 1>&2
python ./parse_items2json.py < "../data/$NAME/dev.json" > "../data/$NAME/dev.json.parsed"
echo "parsed validation data" 1>&2
python ./make_vocab_list.py -t 0 < "../data/$NAME/train.json.parsed" > "../data/$NAME/vocab.txt"
echo "vocabulary created.." 1>&2
