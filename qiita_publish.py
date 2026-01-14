import os
import requests
from   dotenv   import load_dotenv

QIITA_API_URL = "https://qiita.com/api/v2/items"
QIITA_TOKEN = os.getenv("QIITA_TOKEN")

def to_qiita_md(i, arxiv_url, title, authors, summary):
#     return f"""
# ---
# ## 論文情報
# - **Title**: {title}
# - **Authors**: {", ".join(auth for auth in authors)}
# - **arXiv**: {arxiv_url}
# ## 論文概要（自動要約）
# {summary}
# """
    return f"""
# 論文紹介:{title}

## 概要（自動翻訳・要約）
{summary}

## 論文情報
- 著者  :{", ".join(auth for auth in authors)}
- 公開日:{published}
- arXiv:{arxiv_url}
---
※本記事は arXiv 論文の非公式な自動翻訳・要約です。
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

if __name__ == "main":
    # test
    print(QIITA_TOKEN)
s    # tst = post_to_qiita(title="Test", body)

    title = "テスト投稿：arXiv論文自動要約"
    body = """
    # テスト

    これはQiita APIからの自動投稿テストです。

    ※本記事は arXiv 論文の非公式な自動翻訳・要約です。
    """
    tags = ["arXiv", "論文", "自動投稿"]

    url = post_to_qiita(title, body, tags, private=True)
    print(url)
