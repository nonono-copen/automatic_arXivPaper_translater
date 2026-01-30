import os
import requests

QIITA_API_URL = "https://qiita.com/api/v2/items"
QIITA_TOKEN = os.getenv("QIITA_TOKEN") # 環境変数からQiitaトークンを取得

if not QIITA_TOKEN:
    raise RuntimeError("QIITA_TOKEN is not set")

QIITA_TOKEN = QIITA_TOKEN.strip()  # 空白や改行を削除


def make_intro_md(date):
    return f"""
# はじめに／注意書き
本記事は、arXivのComputer Vision & Pattern Recognitionの最新論文を自動取得し、AIで自動要約＆翻訳したものを自動投稿している。
仕組み：xxxx

論文は{date}時点のarXiv最新論文である。
AIで要約＆翻訳されているため、一部翻訳されていなかったり、間違った表現や内容になっている。
鵜呑みにせず、しっかりと自分の目で見極めてほしい。注意書きは以上！
"""

def to_qiita_md(arxiv_id, arxiv_url, title, authors, summary_ja, published,original_s):
    md = f"""
# {title}
- 著者  :{", ".join(auth for auth in authors)}
## 概要
{summary_ja["overview"]}

## 従来研究と比べて何が新しい？
{summary_ja["novelty"]}

## 技術・手法のキモ
{summary_ja["key_method"]}

## 有効性の検証方法
{summary_ja["evaluation"]}

## 議論・課題
{summary_ja["limitations"]}

## 論文情報
- 公開日:{published}
- arXiv_ID:{arxiv_id}
- URL:{arxiv_url}

<details><summary>原文サマリ</summary>
{original_s}
</details>
"""
    return md

def post_to_qiita(title, body, tags, private=False):
    headers = {
        "Authorization": f"Bearer {QIITA_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "title": title,
        "body": body,
        "private": private,
        "tags": [{"name": tag} for tag in tags]
    }

    response = requests.post(QIITA_API_URL, headers=headers, json=payload)

    if response.status_code == 201:
        print("✅ Qiita投稿成功")
        return response.json()["url"]
    else:
        print("❌ Qiita投稿失敗")
        print(response.status_code)
        print(response.text)
        return None



if __name__ == '__main__':
    # test
    print(QIITA_TOKEN)

    title = "テスト投稿：arXiv論文自動要約"
    body = """
    # テスト

    これはQiita APIからの自動投稿テストです。

    ※本記事は arXiv 論文の非公式な自動翻訳・要約です。
    """
    tags = ["arXiv", "論文", "自動投稿"]

    url = post_to_qiita(title, body, tags, private=True)
    print(url)
