#######################################################################
# abstract  指定した{text}を、ollamaで要約または翻訳を行う
#######################################################################
import ollama
import time
from   tqdm import tqdm
import json

MODEL_SUMMARY   = "phi3:mini" # 軽量モデル
MODEL_TRANSLATE = "qwen2.5:1.5b"

def progress_display(stream):
    # cheak progress
    start = time.time()
    chunks = 0
    result_chunks = []

    pbar = tqdm(
        desc="Generating",
        unit="chunks",
        mininterval=0.3,
    )

    for chunk in stream:
        if chunk.get("done"):
            break

        text = chunk.get("response", "")
        if not text:
            continue

        result_chunks.append(text)

        chunks += 1
        pbar.update(1)

        # chunks/s を間引き表示
        if chunks % 5 == 0:
            elapsed = time.time() - start
            pbar.set_postfix(speed=f"{chunks/elapsed:.2f} ch/s")
    pbar.close()

    # ===== 生成完了後 =====
    result_text = "".join(result_chunks)

    print("\n=== Generation Result ===")
    print(result_text)
    return result_text

def warmup_model():
    print("Start warmup models")
    try:
        res=ollama.generate(
            model=MODEL_SUMMARY,
            prompt=".",
            options={"num_predict": 1} #1トークン出力して終了
        )
        # ollama.generate(
        #     model=MODEL_TRANSLATE,
        #     prompt="warmup",
        #     options={"temperature": 0}
        # )
    except:
        pass
    print("Finish warm up models")


# --- Step 1: 構造化要約（at 英語） ---
def structure_summary_en(summary: str) -> dict:
    prompt = f"""
                You are an academic paper analyzer.

                Extract information ONLY from the input.
                Do NOT add assumptions.
                
                Return STRICT JSON only.
                Do NOT change JSON Keys.
                No markdown.
                No explanation.
                
                JSON format:
                {{
                    "overview": "",
                    "novelty": "",
                    "key_method": "",
                    "evaluation": "",
                    "limitations": ""
                }}
            === INPUT START ===
            {summary}
            === INPUT END ===
        """
    res = ollama.generate(
        model   = MODEL_SUMMARY,
        prompt  = prompt,
        stream  = True,
        options = {"temperature": 0.2}
    )
    result = progress_display(res)
    return json.loads(result)

# # --- Step 2: 日本語翻訳 ---
# #######################################################################
# # args      text    : 要約対象の文章
# # return    res     : ollamaからの回答結果
# #######################################################################
def translate_text_ja(text: str) -> str:
    if not text.strip():
        return ""

    prompt = f"""
        Translate the following academic text into natural Japanese.
        Do NOT summarize.
        Do NOT add information.
        Return translation only.
        === INPUT START ===
        {text}
        === INPUT END ===
    """
    res = ollama.generate(
        # model=MODEL_TRANSLATE,
        model   = MODEL_SUMMARY, # Codespaces等の軽量環境向けに軽量モデルを使用
        prompt=prompt,
        stream=True,
        options={"temperature": 0.2}
    )
    result = progress_display(res)

    return result



def translate_json_ja(data: dict) -> dict:
    translated = {}
    for key in ["overview", "novelty", "key_method", "evaluation", "limitations"]:
        value = str(data.get(key, "")) # 中身が辞書型で渡されることを備えstr()で変換
        translated[key] = translate_text_ja(value)
    return translated


if __name__ == "__main__":
    # PROMPT = "日本の少子化問題について分かりやすく説明してください。"
    # stream = ollama.generate(
    #     model  = MODEL,
    #     prompt = PROMPT,
    #     stream = True,
    # )
    # result = progress_display(stream)

    sample_text = """
        Arabic calligraphy represents one of the richest visual traditions of the Arabic language, blending linguistic meaning with artistic form. Although multimodal models have advanced across languages, their ability to process Arabic script, especially in artistic and stylized calligraphic forms, remains largely unexplored. To address this gap, we present DuwatBench, a benchmark of 1,272 curated samples containing about 1,475 unique words across six classical and modern calligraphic styles, each paired with sentence-level detection annotations. The dataset reflects real-world challenges in Arabic writing, such as complex stroke patterns, dense ligatures, and stylistic variations that often challenge standard text recognition systems. Using DuwatBench, we evaluated 13 leading Arabic and multilingual multimodal models and showed that while they perform well on clean text, they struggle with calligraphic variation, artistic distortions, and precise visual-text alignment. By publicly releasing DuwatBench and its annotations, we aim to advance culturally grounded multimodal research, foster fair inclusion of the Arabic language and visual heritage in AI systems, and support continued progress in this area. Our dataset (https://huggingface.co/datasets/MBZUAI/DuwatBench) and evaluation suit (https://github.com/mbzuai-oryx/DuwatBench) are publicly available.
    """

    # 落合陽一フォーマットに合わせてsummaryをさらに要約 with ollama
    summary_en = structure_summary_en(sample_text)
    print(type(summary_en))
    # 要約した文章群を翻訳 with ollama
    summary_ja = translate_json_ja(summary_en)