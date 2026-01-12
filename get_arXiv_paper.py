#######################################################################
# abstract  指定した{category}の最新論文を、{max_results}分取得する
# args      category    : 指定カテゴリ(def cs.CL(計算言語学)),
#           max_results : 最大取得論文数(def 3)
# return    paper       :
#######################################################################

import feedparser

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
