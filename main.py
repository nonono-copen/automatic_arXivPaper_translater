#######################################################################
# abstract  arXivの最新論文を落合洋一フォーマットにまとめて翻訳し、Qiitaに投稿
#           ・最新論文の取得はarXiv APIを使用
#           ・論文要約および翻訳にはOllamaのモデルを使用
#           ・論文の要約は落合陽一フォーマットにまとめる
#           ・Qiitaへの投稿にはQiita APIを使用(投稿は非公開設定)
# 　　　　　　・Qiitaへの投稿済か否かは論文IDで重複チェック
# 　　　　　　・投稿管理用にCSVファイルを作成し、投稿履歴を管理
#           ・開発者はRaspberry Pi4やCodespaces等での軽量環境を想定（これ重要）
# date      2026/01/30
#######################################################################

from datetime               import date
from models.ollama_AI       import structure_summary_en, translate_json_ja,warmup_model
from utils.get_arXiv_paper  import fetch_latest_arxiv
from utils.manage_log       import init_csv, is_already_posted, log_post
from utils.qiita_publish    import make_intro_md,to_qiita_md, post_to_qiita


# --- 定数 ---
CATEGORY    = "cs.CV" # arXivカテゴリ ComputerVision&PatternRecognition
MAX         = 2       # 取得論文数
QIITA_TAGS  = ["arXiv", "論文", "自動投稿"]      # Qiiita投稿用投稿用タグ
DATE        = str(date.today())                # 投稿日付
QIITA_TITLE = 'arXiv論文自動要約 投稿日：' + DATE # Qiiita投稿用投稿用タイトル


init_csv()                     # 投稿管理用CSVの準備
mds = make_intro_md(date=DATE) # 投稿用markdown格納用
warmup_model()                 # ollama model事前起動(ラスパイ等で初回起動が遅い場合対策)
url = None                     # Qiita投稿URL格納用（投稿失敗時はNoneのまま）
i    = 0                       # 処理論文数カウンタ
logs = []                      # 投稿ログ格納用リスト

# --- arXiv APIで最新論文情報を取得 ---
papers = fetch_latest_arxiv(category=CATEGORY, max_results=MAX)

for p in papers:
    i +=1
    pid = p["id"]
    print(f"{i}: {pid}")

    # 過去に取得した論文IDと重複チェック
    if is_already_posted(arxiv_id = pid):
        print(f"Skip:{pid} is already posted")
        continue # 投稿済論文IDならばスキップ    

    # 落合陽一フォーマットに合わせてsummaryをさらに要約 with ollama
    summary_en = structure_summary_en(p["summary"])

    # 要約した文章群を翻訳 with ollama
    summary_ja = translate_json_ja(summary_en)

    # TODO:論文内の1枚目画像を抽出

    # markdownに変換 ＆ Qiita apiで投稿
    md = to_qiita_md(
        arxiv_id   = p["id"],
        arxiv_url  = p["url"], 
        title      = p["title"], 
        authors    = p["authors"], 
        summary_ja = summary_ja, 
        published  = p["published"],
        original_s = p["summary"])
    mds += md    # 複数論文をまとめて投稿する場合に備えて連結

    # log記録｀
    logs.append({
        "arxiv_id"  : pid,
        "title"     : p["title"],
        "summary_ja": summary_ja,
        "qiita_url" : "",
        "status"    : "pending"
    })


# Qiitaに投稿 （コメントアウト状態の場合、CSVログだけ保存）
# url = post_to_qiita(title  =QIITA_TITLE,
#                     body   =mds,
#                     tags   =QIITA_TAGS,
#                     private=True)

# 投稿成功／失敗の判定
if url == None:
    status = False
else:
    status = True

# 投稿内容＆結果をCSVに反映
for log in logs:
    log_post(
        arxiv_id   = log["arxiv_id"],
        title      = log["title"],
        summary_ja = log["summary_ja"],
        qiita_url  = url if status else "",
        status     = "success" if status else "failed"
    )









