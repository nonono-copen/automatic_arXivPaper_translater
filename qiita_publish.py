import requests
import os

def to_qiita_md(arxiv_id, title, authors, summary):
    return f"""
---
## 論文情報
- **Title**: {title}
- **Authors**: {", ".join(auth for auth in authors)}
- **arXiv**: {arxiv_id}
## 論文概要（自動要約）
{summary}
"""



def post_qiita(title, body, tags=["arXiv"]):
    token = os.environ["QIITA_TOKEN"]

    url = "https://qiita.com/api/v2/items"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "title": title,
        "body": body,
        "tags": [{"name": t} for t in tags],
        "private": False
    }
    r = requests.post(url, headers=headers, json=payload)
    r.raise_for_status()
