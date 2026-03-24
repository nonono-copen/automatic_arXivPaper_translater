"""
ローカルPC → GitHub → Qiita 画像付き記事自動投稿スクリプト

リポジトリ構成:
  automatic_arXiv_translate/
    ┣ {date1}/
    ┃  ┣ {arXiv_id1}_figure.jpg
    ┃  ┗ {arXiv_id2}_figure.jpg
    ┗ {date2}/
       ┗ ...
"""
import os
import time
import base64
import requests
from datetime import datetime,date
from pathlib import Path
from PIL import Image
import io

# ============================================================
# 設定（.envまたは環境変数から読み込む）
# ============================================================
TOKEN_GITHUB    = os.environ["TOKEN_GITHUB"]
USER_GITHUB     = os.environ["USER_GITHUB"]
REPO_GITHUB     = os.environ["REPO_GITHUB"]      # 例: "qiita-images"
BRANCH_GITHUB   = os.environ.get("BRANCH_GITHUB", "main")
QIITA_TOKEN     = os.environ["QIITA_TOKEN"]

# GitHubリポジトリ内のベースパス
REPO_BASE_PATH  = "automatic_arXiv_translate"

# ============================================================
# 画像圧縮
# ============================================================
def compress_image(image_path: Path, quality: int = 85) -> bytes:
    """
    画像をJPEG形式で圧縮してバイナリを返す。
    - 100KB以下の場合はそのまま返す
    """
    with Image.open(image_path) as img:
        # RGBAはJPEG非対応なのでRGBに変換
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        original_size = image_path.stat().st_size
        if original_size <= 100 * 1024:
            # 小さい画像はそのまま
            return image_path.read_bytes()

        output = io.BytesIO()
        img.save(output, format="JPEG", quality=quality, optimize=True)
        return output.getvalue()


# ============================================================
# GitHub API
# ============================================================
def build_raw_url(repo_path: str) -> str:
    return (
        f"https://raw.githubusercontent.com/"
        f"{USER_GITHUB}/{REPO_GITHUB}/{BRANCH_GITHUB}/{repo_path}"
    )

def upload_image_to_github(image_binary: bytes, repo_path: str, dry_run: bool = False) -> str:
    """
    GitHubリポジトリに画像をアップロードし、raw URLを返す。
    既に同じパスにファイルが存在する場合は上書きしない（スキップ）。

    repo_path 例: "automatic_arXiv_translate/20240301/2403.12345_figure.jpg"
    """
    url = f"https://api.github.com/repos/{USER_GITHUB}/{REPO_GITHUB}/contents/{repo_path}"
    headers = {
        "Authorization": f"Bearer {TOKEN_GITHUB}",
        "Accept": "application/vnd.github+json",
    }

    if dry_run:
        print(f"  [DRY RUN] GitHub upload skipped: {repo_path}")
        return build_raw_url(repo_path)

    # 既存ファイルのSHAを取得（上書き時に必要）
    get_resp = requests.get(url, headers=headers)
    sha = get_resp.json().get("sha") if get_resp.status_code == 200 else None

    if sha:
        print(f"  既にGitHubに存在します。スキップ: {repo_path}")
        return build_raw_url(repo_path)

    encoded = base64.b64encode(image_binary).decode("utf-8")
    payload = {
        "message": f"Add {repo_path}",
        "content": encoded,
        "branch": BRANCH_GITHUB,
    }

    resp = requests.put(url, headers=headers, json=payload)
    resp.raise_for_status()
    print(f"  ✅ GitHubアップロード完了: {repo_path}")

    time.sleep(0.5)  # 連続アップロード防止
    return build_raw_url(repo_path)


# ============================================================
# Qiita API
# ============================================================
def post_to_qiita(title: str, body: str, tags: list[str], private: bool = True) -> dict:
    """
    Qiitaに記事を投稿する。
    private=True の場合は限定公開（確認後に手動で公開推奨）。
    """
    resp = requests.post(
        "https://qiita.com/api/v2/items",
        headers={
            "Authorization": f"Bearer {QIITA_TOKEN}",
            "Content-Type": "application/json",
        },
        json={
            "title": title,
            "body": body,
            "private": private,
            "tags": [{"name": t, "versions": []} for t in tags],
        },
    )
    resp.raise_for_status()
    return resp.json()

# def update_qiita_article(item_id: str, title: str, body: str, tags: list[str]) -> dict:
#     """既存Qiita記事を更新する。"""
#     resp = requests.patch(
#         f"https://qiita.com/api/v2/items/{item_id}",
#         headers={
#             "Authorization": f"Bearer {QIITA_TOKEN}",
#             "Content-Type": "application/json",
#         },
#         json={
#             "title": title,
#             "body": body,
#             "tags": [{"name": t, "versions": []} for t in tags],
#         },
#     )
#     resp.raise_for_status()
#     return resp.json()


# ============================================================
# Markdown本文生成
# ============================================================
def build_article_body(
    date: str,
    arxiv_entries: list[dict],
) -> str:
    """
    arxiv_entries: [
        {
            "arxiv_id": "2403.12345",
            "title": "論文タイトル",
            "abstract_ja": "日本語アブスト",
            "image_url": "https://raw.githubusercontent.com/..."
        },
        ...
    ]
    """
    lines = [
        f"# arXiv 自動翻訳まとめ ({date})",
        "",
        f"> 投稿日: {datetime.now().strftime('%Y-%m-%d %H:%M')}  ",
        f"> 対象日付: {date}",
        "",
        "---",
        "",
    ]

    for entry in arxiv_entries:
        arxiv_id   = entry["arxiv_id"]
        title      = entry.get("title", arxiv_id)
        abstract   = entry.get("abstract_ja", "")
        image_url  = entry.get("image_url", "")
        arxiv_url  = f"https://arxiv.org/abs/{arxiv_id}"

        lines += [
            f"## {title}",
            "",
            f"**arXiv:** [{arxiv_id}]({arxiv_url})",
            "",
        ]

        if image_url:
            lines += [
                f"![{arxiv_id} figure]({image_url})",
                "",
            ]

        if abstract:
            lines += [
                "### 概要",
                "",
                abstract,
                "",
            ]

        lines += ["---", ""]

    return "\n".join(lines)


# ============================================================
# メイン処理
# ============================================================
def process_date_folder(
    local_date_dir: Path,
    arxiv_metadata: dict,
    tags: list[str] = None,
    private: bool = True,
    dry_run: bool = False,
) -> dict | None:
    """
    1つの日付フォルダを処理してQiitaに投稿する。

    local_date_dir : Path  例: ./images/20240301
    arxiv_metadata : dict  arXiv IDをキーにしたメタ情報
                           例: {"2403.12345": {"title": "...", "abstract_ja": "..."}}
    """
    date = local_date_dir.name  # フォルダ名 = 日付
    tags = tags or ["arXiv", "機械学習", "論文紹介", "自動翻訳"]

    image_files = sorted(local_date_dir.glob("*_figure.jpg"))
    if not image_files:
        print(f"[{date}] 画像ファイルが見つかりません。スキップ。")
        return None

    print(f"\n📁 処理開始: {date} ({len(image_files)}件)")

    arxiv_entries = []
    for img_path in image_files:
        # ファイル名から arXiv IDを抽出 (例: 2403.12345_figure.jpg → 2403.12345)
        arxiv_id = img_path.stem.replace("_figure", "")

        # GitHub上のパス
        repo_path = f"{REPO_BASE_PATH}/{date}/{img_path.name}"

        # 圧縮 → GitHub アップロード
        print(f"  処理中: {img_path.name}")
        compressed = compress_image(img_path)
        image_url  = upload_image_to_github(compressed, repo_path, dry_run=dry_run)

        # メタ情報をマージ
        meta = arxiv_metadata.get(arxiv_id, {})
        arxiv_entries.append({
            "arxiv_id":    arxiv_id,
            "title":       meta.get("title", f"arXiv:{arxiv_id}"),
            "abstract_ja": meta.get("abstract_ja", ""),
            "image_url":   image_url,
        })

    # Markdown本文生成
    body  = build_article_body(date, arxiv_entries)
    title = f"【arXiv翻訳】{date} 論文まとめ ({len(arxiv_entries)}件)"

    if dry_run:
        print(f"\n[DRY RUN] Qiita投稿スキップ")
        print(f"  タイトル: {title}")
        print(f"  本文プレビュー:\n{body[:300]}...")
        return {"title": title, "body": body}

    # Qiita投稿
    print(f"\n🚀 Qiitaに投稿中...")
    result = post_to_qiita(title, body, tags, private=private)
    print(f"  ✅ 投稿完了: {result['url']}")
    return result


def run(
    local_base_dir: str = "./images",
    arxiv_metadata: dict = None,
    tags: list[str] = None,
    private: bool = True,
    dry_run: bool = False,
    target_dates: list[str] = None,
):
    """
    local_base_dir 配下の日付フォルダを順番に処理する。

    target_dates: 指定した場合はその日付のみ処理
                  例: ["20240301", "20240302"]
    """
    base = Path(local_base_dir)
    if not base.exists():
        raise FileNotFoundError(f"ディレクトリが見つかりません: {base}")

    arxiv_metadata = arxiv_metadata or {}
    date_dirs = sorted([d for d in base.iterdir() if d.is_dir()])

    if target_dates:
        date_dirs = [d for d in date_dirs if d.name in target_dates]

    if not date_dirs:
        print("処理対象のフォルダがありません。")
        return

    results = []
    for date_dir in date_dirs:
        result = process_date_folder(
            date_dir,
            arxiv_metadata=arxiv_metadata,
            tags=tags,
            private=private,
            dry_run=dry_run,
        )
        if result:
            results.append(result)
        time.sleep(1)  # Qiita API レート制限対策

    print(f"\n🎉 完了: {len(results)}件の記事を投稿しました。")
    return results


# ============================================================
# 実行例
# ============================================================
if __name__ == "__main__":
    # arXiv論文のメタ情報（別途取得・生成したものを渡す）
    # sample_metadata = {
    #     "2403.12345": {
    #         "title":       "大規模言語モデルの効率的なファインチューニング手法",
    #         "abstract_ja": "本研究では、計算コストを削減しながら高精度を維持する新しいファインチューニング手法を提案する。",
    #     },
    #     "2403.67890": {
    #         "title":       "Vision Transformerを用いた医療画像診断",
    #         "abstract_ja": "Vision Transformerアーキテクチャを医療画像診断に適用し、従来手法を上回る精度を達成した。",
    #     },
    # }

    # run(
    #     local_base_dir="./images",       # ローカルの画像フォルダ
    #     arxiv_metadata=sample_metadata,
    #     tags=["arXiv", "機械学習", "深層学習", "論文紹介"],
    #     private=True,                    # まず限定公開で確認
    #     dry_run=False,                   # Trueにすると実際の投稿なし（テスト用）
    #     target_dates=None,               # Noneで全日付、["20240301"]で特定日のみ
    # )

    # 画像アップロードテスト
    # GitHub上のパス
    img_path = Path("/workspaces/automatic_arXivPaper_translater/extracted_figures/overview_figure_1_page_1.png")
    img_name = os.path.basename(img_path)
    date = date.today()

    repo_path = f"{REPO_BASE_PATH}/{date}/{img_name}"

    # 圧縮 → GitHub アップロード
    print(f"  処理中: {img_name}")
    compressed = compress_image(img_path)
    image_url  = upload_image_to_github(compressed, repo_path, dry_run=False)
    print(image_url)
