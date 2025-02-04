from transformers import pipeline

def analyze_sentiment(texts):
    """
    使用 Hugging Face Transformers 進行情緒分析（支援中文）。
    
    參數:
    - texts (list): 要分析的文字列表
    
    回傳:
    - results (dict): 包含原始文本與情緒分析結果的字典
    """

    # 初始化情緒分析模型
    sentiment_analyzer = pipeline("sentiment-analysis", model="uer/roberta-base-finetuned-jd-binary-chinese")

    # 儲存分析結果
    results = {}

    for text in texts:
        result = sentiment_analyzer(text)
        results[text] = result[0]  # 取出結果並存入字典

    return results

# 測試函式
if __name__ == "__main__":
    sample_texts = [
        "這個產品真的很棒！我非常喜歡。",
        "這是我用過最糟糕的服務。",
        "還可以，沒什麼特別的感覺。"
    ]

    sentiment_results = analyze_sentiment(sample_texts)

    for text, analysis in sentiment_results.items():
        print(f"文本: {text}")
        print(f"情緒分析結果: {analysis}\n")
