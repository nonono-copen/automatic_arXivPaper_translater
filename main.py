#######################################################################
# abstract  arXivの最新論文を落合洋一フォーマットにまとめて翻訳し、Qiitaに投稿
# 　　　　　　・Qiitaへの投稿済か否かは論文IDで重複チェック
# 　　　　　　・arXiv Sanityを使った「注目論文抽出」設計をする
# 　　　　　　・論文の一枚目画像も投稿対象とする Qiita投稿時は規約違反となるため含めない
#           ・翻訳／要約に利用する生成AIは、____とする。
#######################################################################
from get_arXiv_paper import fetch_latest_arxiv
from ollama_AI       import structure_summary_en, translate_ja
from qiita_publish   import to_qiita_md
from post_log        import init_csv, is_already_posted, log_post

# --- 定数 ---
CATEGORY = "cs.CV"
MAX      = 3

# 管理ファイルチェック
init_csv()

### 最新論文のまとめ ###
# --- arXiv APIで最新論文情報を取得 ---
papers = fetch_latest_arxiv(category=CATEGORY, max_results=MAX)

for p in papers:
    # print("ID:"      + p["id"])
    # print("TITLE:"   + p["title"])
    # print("SUMMARY:" + p["summary"])
    # print("AUTHORS:" )
    # for auth in p["authors"]: print(auth)
    # print("URL:"     + p["url"])
    # print("投稿日:"   + p["published"]) 

    # 過去に取得した論文IDと重複チェック
    if is_already_posted(arxiv_id = p["id"]):
        print(f"Skip: {p["id"]} is already posted")
        # log_post(p["id"], p["title"], "", "skipped")
        continue # 投稿済論文IDならばスキップ    

    # 落合陽一フォーマットに合わせてsummaryをさらに要約 with ollama
    summary_en = structure_summary_en(p["summary"])
    print(summary_en)

    # 要約した文章群を翻訳 with ollama
    summary_ja = translate_ja(summary_en)
    print(summary_ja)

    # CHARANGE:論文内の1枚目画像を抽出

    # markdownに変換 ＆ Qiita apiで投稿
    md = to_qiita_md(arxiv_id=p["id"], title=p["title"], authors=p["authors"], summary=summary_ja)
    print(md)  # ← Qiita投稿前の最終成果物

    # 管理ファイルに投稿内容を記録｀
    log_post(p["id"], p["title"], summary_ja, "dummy", "test")

    






### 注目度の高い論文を収集 ###
# TODO:arXiv Sanityで注目度が高い論文を抽出

# --- 該当論文をarXiv APIで情報を取得 ---
# papers = fetch_latest_arxiv(category=CATEGORY, max_results=MAX)
    
# TODO:過去に取得した論文IDと重複チェック

# TODO:落合陽一フォーマットに合わせてsummaryをさらに要約

# TODO:要約した文章群を翻訳

# CHARANGE:論文内の1枚目画像を抽出

# TODO:Qiita apiで投稿
