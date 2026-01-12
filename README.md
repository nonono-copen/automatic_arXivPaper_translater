# automatic_arXivPaper_translater
## Abstract/このソースって何物？
This source is an efficiency tool for arXiv paper.
This tool summarizes the latest papers submitted in designated categories on arXiv in Yoichi Ochiai's format and summarizes them in Japanese.

arXivの指定カテゴリで投稿された最新論文を、落合陽一フォーマットで要約し、日本語に要約することで、論文をより早く読むツールである。

参考：[高速で論文がバリバリ読める落合先生のフォーマットがいい感じだったのでメモ](https://lafrenze.hatenablog.com/entry/2015/08/04/120205)

## Setup/
### 1. Install library/ライブラリセットアップ
```
pip install -r requirements.txt
```

### 2. Setup ollama AI/ollamaのセットアップ
```
./setup.sh # install ollama AI models
```

## Execution/実行方法
```
python main.py
```

## Output/出力
output to post_log.csv

CSVに出力される（開発者はQiitaへの自動投稿も実施）
| arxiv_id | title | summary | posted_at | qiita_url | status |
|:-----------:|:------------:|:------------:|:------------:|:------------:|:------------:|
| 論文ID       | タイトル        | 日本語サマリ | 投稿日 | 投稿先URL | 投稿状況 |
