import requests
import fitz  # PyMuPDF
from pathlib import Path
from PIL import Image
import io

# =====================
# 設定
# =====================
KEYWORDS = [
    "overview",
    "architecture",
    "pipeline",
    "framework",
    "model"
]

MAX_PAGES = 3  # 先頭Nページのみ解析


# =====================
# arXiv PDF ダウンロード
# =====================
def download_arxiv_pdf(arxiv_url: str, out_dir="pdf"):
    out_dir = Path(out_dir)
    out_dir.mkdir(exist_ok=True)

    if "/abs/" in arxiv_url:
        pdf_url = arxiv_url.replace("/abs/", "/pdf/") + ".pdf"
    else:
        pdf_url = arxiv_url

    pdf_path = out_dir / "paper.pdf"

    r = requests.get(pdf_url, timeout=30)
    r.raise_for_status()
    pdf_path.write_bytes(r.content)

    return pdf_path


# =====================
# 画像抽出 + メタ情報取得
# =====================
def extract_images_with_metadata(pdf_path):
    doc = fitz.open(pdf_path)
    candidates = []

    for page_index in range(min(len(doc), MAX_PAGES)):
        page = doc[page_index]
        page_text = page.get_text("text").lower()

        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base = doc.extract_image(xref)

            image_bytes = base["image"]
            image = Image.open(io.BytesIO(image_bytes))
            width, height = image.size

            candidates.append({
                "page": page_index + 1,
                "index": img_index + 1,
                "width": width,
                "height": height,
                "area": width * height,
                "aspect": width / height,
                "page_text": page_text,
                "image_bytes": image_bytes,
                "ext": base["ext"]
            })

    return candidates


# =====================
# 概要図スコアリング
# =====================
def score_image(candidate):
    score = 0

    # 前半ページ優遇
    if candidate["page"] == 1:
        score += 3
    elif candidate["page"] == 2:
        score += 2

    # サイズ（大きい図を優先）
    score += candidate["area"] / 1e6

    # 横長ボーナス
    if candidate["aspect"] > 1.2:
        score += 2

    # キーワード
    for kw in KEYWORDS:
        if kw in candidate["page_text"]:
            score += 3

    return score


# =====================
# 概要図を1枚選択して保存
# =====================
def select_overview_image(pdf_path, out_dir="images"):
    out_dir = Path(out_dir)
    out_dir.mkdir(exist_ok=True)

    candidates = extract_images_with_metadata(pdf_path)
    if not candidates:
        return None

    best = max(candidates, key=score_image)

    out_path = out_dir / f"overview_page{best['page']}.{best['ext']}"
    out_path.write_bytes(best["image_bytes"])

    return out_path


# =====================
# メイン処理
# =====================
if __name__ == "__main__":
    arxiv_url = "https://arxiv.org/pdf/2601.10716v1"

    print("PDFをダウンロード中...")
    pdf_path = download_arxiv_pdf(arxiv_url)

    print("概要図を自動選択中...")
    overview_image = select_overview_image(pdf_path)

    if overview_image:
        print(f"概要図を保存しました: {overview_image}")
    else:
        print("概要図候補が見つかりませんでした")