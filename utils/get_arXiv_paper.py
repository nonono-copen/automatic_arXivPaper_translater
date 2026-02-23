import os
from   pathlib    import Path
import feedparser
import requests

#######################################################################
# 指定した{category}の最新論文の情報を、{max_results}分取得する
#######################################################################
def fetch_latest_arxiv(category="cs.CL", max_results=3):
    query = f"http://export.arxiv.org/api/query?search_query=cat:{category}&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"
    feed = feedparser.parse(query)

    papers = []
    for entry in feed.entries:
        papers.append({
            "id"        : entry.id.split("/abs/")[-1],
            "title"     : entry.title.replace("\n", " "),
            "summary"   : entry.summary.replace("\n", " "),
            "authors"   : [author.name for author in entry.authors],
            "url"       : entry.link,
            "published" : entry.published
        })

    return papers


#######################################################################
# 指定したURLから論文をダウンロードする
#######################################################################
def download_pdf(url, output_dir, pdf_name):
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    try:
        # URLからPDFを取得
        response = requests.get(url, stream=True)
        response.raise_for_status()  # エラーチェック
        
        save_path = os.path.join(output_dir, pdf_name)
        # ファイルとして保存
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"ダウンロード完了: {save_path}")
        return save_path

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None



if __name__ == '__main__':
    PDF_DIR = './pdf/'

    # --- arXiv APIで最新論文情報を取得 ---
    papers = fetch_latest_arxiv(category='cs.CV', max_results=2)

    for p in papers:
        id = p['id']
        pdf_name = id + '.pdf'
        url = f"https://arxiv.org/pdf/{id}.pdf"
        print(url)
        _ = download_pdf(url, PDF_DIR, pdf_name)

