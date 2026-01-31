#######################################################################
# abstract  管理用の一時ファイル（csv）の作成および管理操作
#######################################################################
import csv
import os
from   datetime import datetime

CSV_PATH    = "post_log.csv"
FIELDS      = ["arxiv_id", "title", "summary", "posted_at", "qiita_url", "status"]

#######################################################################
# 初回時にCSVを生成
#######################################################################
def init_csv():
    # CSVファイルが存在しない場合、新規作成
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()

#######################################################################
# abstract  投稿済論文のチェック
# args      arxiv_id    : csv内の投稿済論文ID
# return    csvファイルへの追記成否（csvファイルがない場合はFalse）
#######################################################################
def is_already_posted(arxiv_id: str) -> bool:
    if not os.path.exists(CSV_PATH):
        return False

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return any(row["arxiv_id"] == arxiv_id and row["status"] == "success" for row in reader)

#######################################################################
# abstract  投稿内容をcsvに記録
# args      arxiv_id    :論文ID
#           title       :論文タイトル
#           qiita_url   :Qiita投稿先URL
#           status      :失敗時の再実行判定
#######################################################################
def log_post(arxiv_id, title, summary_ja,  qiita_url, status):
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writerow({
            "arxiv_id": arxiv_id,
            "title": title,
            "summary": summary_ja,
            "posted_at": datetime.utcnow().isoformat(),
            "qiita_url": qiita_url,
            "status": status,
        })


if __name__ == '__main__':
    # test
    init_csv()
    # log_post(
    #     arxiv_id  = "2301.00001",
    #     title     = "Test Paper",
    #     summary_ja= "これはテスト要約です。",
    #     qiita_url = "https://qiita.com/test_paper",
    #     status    = "success"
    # )
    # print(is_already_posted("2301.00001"))  # True
    # print(is_already_posted("2301.00002"))  # False


