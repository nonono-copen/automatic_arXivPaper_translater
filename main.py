#######################################################################
# abstract  arXivの最新論文を翻訳し、落合洋一フォーマットにまとめ、Qiitaに投稿
#             TODO
# 　　　　　　     ・Qiitaへの投稿済か否かは論文IDで重複チェック
# 　　　　　　     ・arXiv Sanityを使った「注目論文抽出」設計をする
# 　　　　　　     ・論文の一枚面の画像も（自分用での）投稿対象とする
#######################################################################
from get_arXiv_paper import fetch_latest_arxiv

CATEGORY = "cs.CV"
MAX      = 3


### 最新論文のまとめ ###
# --- arXiv APIで最新論文情報を取得 ---
papers = fetch_latest_arxiv(category=CATEGORY, max_results=MAX)

# test: 取得した論文情報を表示
# for p in papers:
#     print("ID:"      + p["id"])
#     print("TITLE:"   + p["title"])
#     print("SUMMARY:" + p["summary"])
#     print("AUTHORS:" + p["authors"])
#     print("URL:"     + p["url"])
#     print("投稿日:"   + p["published"]) 
    

# TODO:過去に取得した論文IDと重複チェック

# TODO:落合陽一フォーマットに合わせてsummaryをさらに要約

# TODO:要約した文章群を翻訳

# CHARANGE:論文内の1枚目画像を抽出

# TODO:Qiita apiで投稿


### 注目度の高い論文を収集 ###
# TODO:arXiv Sanityで注目度が高い論文を抽出

# --- 該当論文をarXiv APIで情報を取得 ---
# papers = fetch_latest_arxiv(category=CATEGORY, max_results=MAX)

# test: 取得した論文情報を表示
# for p in papers:
#     print("ID:"      + p["id"])
#     print("TITLE:"   + p["title"])
#     print("SUMMARY:" + p["summary"])
#     print("AUTHORS:" + p["authors"])
#     print("URL:"     + p["url"])
#     print("投稿日:"   + p["published"]) 
    

# TODO:過去に取得した論文IDと重複チェック

# TODO:落合陽一フォーマットに合わせてsummaryをさらに要約

# TODO:要約した文章群を翻訳

# CHARANGE:論文内の1枚目画像を抽出

# TODO:Qiita apiで投稿
