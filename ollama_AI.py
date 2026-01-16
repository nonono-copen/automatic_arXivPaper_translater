#######################################################################
# abstract  指定した{text}を、ollamaで要約または翻訳を行う
#######################################################################
import ollama

# MODEL_SUMMARY   = "phi3:mini" # 軽量モデル
# MODEL_TRANSLATE = "qwen2.5"   # 日本語翻訳・整形で中規模モデルの中で事故りにくい
MODEL = "qwen2.5:1.5b"

# --- Step 1: 英語要約 ---
#######################################################################
# args      text    : 翻訳対象の文章
# return    res     : ollamaからの回答結果
#######################################################################
# def summarize_en(text: str) -> str:
#     res = ollama.chat(
#         model=MODEL_SUMMARY,
#         messages=[
#             {
#                 "role": "system",
#                 "content": (
#                     "You are an expert research assistant. "
#                     "Summarize academic papers accurately."
#                 )
#             },
#             {
#                 "role": "user",
#                 "content": f"""
#                             Summarize the following academic paper in English.
#                             Focus on:
#                                 - overall contribution
#                                 - novelty compared to prior work
#                                 - key methods
#                                 - evaluation
#                                 - limitations
#                             {text[:8000]}
#                             """
#             }
#         ],
#         options={"temperature": 0.2}
#     )
#     return res["message"]["content"]


# --- Step 2: 構造化要約（英語） ---
def structure_summary_en(summary: str) -> str:
    res = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You structure summaries without adding new information."
            },
            {
                "role": "user",
                "content": f"""
                            Based ONLY on the summary below, extract information.
                            Do NOT add assumptions.
                            Format:
                                Overview:
                                Novelty:
                                Key Method:
                                Evaluation:
                                Discussion / Limitations:
                                Summary:{summary}
                            """
            }
        ],
        options={"temperature": 0.1}
    )
    return res["message"]["content"]


# --- Step 3: 日本語翻訳 ---
#######################################################################
# args      text    : 要約対象の文章
# return    res     : ollamaからの回答結果
#######################################################################
def translate_ja(text: str) -> str:
    res = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a professional academic translator."
            },
            {
                "role": "user",
                "content": f"Translate the following text into Japanese:\n{text}"
            }
        ],
        options={"temperature": 0.2}
    )
    return res["message"]["content"]
