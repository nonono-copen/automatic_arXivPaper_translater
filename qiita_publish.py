import os
import requests

QIITA_API_URL = "https://qiita.com/api/v2/items"
QIITA_TOKEN = os.getenv("QIITA_TOKEN")

if not QIITA_TOKEN:
    raise RuntimeError("QIITA_TOKEN is not set")

QIITA_TOKEN = QIITA_TOKEN.strip()  # 空白や改行を削除

def to_qiita_md(arxiv_id, arxiv_url, title, authors, summary, published):
    return f"""
# 論文紹介:{title}
- 著者  :{", ".join(auth for auth in authors)}
## 自動要約・翻訳情報
{summary}
## 論文情報
- 公開日:{published}
- arXiv_ID:{arxiv_id}
- URL:{arxiv_url}
---
"""

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
