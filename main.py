#######################################################################
# abstract  arXivの最新論文を落合洋一フォーマットにまとめて翻訳し、Qiitaに投稿
# 　　　　　　・Qiitaへの投稿済か否かは論文IDで重複チェック
# 　　　　　　・arXiv Sanityを使った「注目論文抽出」設計をする
# 　　　　　　・論文の一枚目画像も投稿対象とする Qiita投稿時は規約違反となるため含めない
#           ・翻訳／要約に利用する生成AIは、____とする。
#######################################################################
from get_arXiv_paper import fetch_latest_arxiv
from ollama_AI       import structure_summary_en, translate_ja
from qiita_publish   import to_qiita_md, post_to_qiita
from post_log        import init_csv, is_already_posted, log_post
from datetime        import date

# --- 定数 ---
CATEGORY    = "cs.CV"
MAX         = 5
# Qiiita投稿用投稿用タイトル&タグ
QIITA_TAGS  = ["arXiv", "論文", "自動投稿"]
QIITA_TITLE = 'arXiv論文自動要約 投稿日：' + str(date.today())
# print(QIITA_TITLE)
# exit()

# 管理ファイルチェック
init_csv()

# 変数
mds = '' # 投稿用markdown格納用

### 最新論文のまとめ ###
# --- arXiv APIで最新論文情報を取得 ---
papers = fetch_latest_arxiv(category=CATEGORY, max_results=MAX)

for p in papers:
    # 過去に取得した論文IDと重複チェック
    if is_already_posted(arxiv_id = p["id"]):
        print(f"Skip: {p["id"]} is already posted")
        continue # 投稿済論文IDならばスキップ    

    # 落合陽一フォーマットに合わせてsummaryをさらに要約 with ollama
    summary_en = structure_summary_en(p["summary"])
    print(summary_en)

    # 要約した文章群を翻訳 with ollama
    summary_ja = translate_ja(summary_en)
    print(summary_ja)

    # TODO:論文内の1枚目画像を抽出


    # markdownに変換 ＆ Qiita apiで投稿
    md = to_qiita_md(arxiv_id=p["id"],arxiv_url=p["url"], title=p["title"], authors=p["authors"], summary=summary_ja, published=p["published"])
    # print(md)  # ← Qiita投稿前の最終成果物
    mds += md + "\n\n---\n\n"  # 複数論文をまとめて投稿する場合に備えて連結


url = post_to_qiita(title  =QIITA_TITLE,
                    body   =mds,
                    tags   =TAQIITA_TAGSGS,
                    private=True)

if url == None:
    status = False
else:
    status = True

# 管理ファイルに投稿内容を記録｀
log_post(arxiv_id=p["id"], title=p["title"], summary_ja=mds, qiita_url=url, status=status)








