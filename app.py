import streamlit as st
import requests
import json
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

# 讀取 .env 檔案中的環境變數
load_dotenv()

# Langchain API 設定
langchain_api_url = os.getenv("LANGCHAIN_API_URL")
api_key = os.getenv("API_KEY")

# 設定頁面標題
st.set_page_config(page_title="對話輸入介面", layout="wide")

# 使用 CSS 調整頁面寬度
st.markdown("""
    <style>
        .block-container {
            max-width: 90% !important;  
            padding-left: 5% !important;
            padding-right: 5% !important;
        }
    </style>
""", unsafe_allow_html=True)

# 初始化 session_state
if "outputs" not in st.session_state:
    st.session_state.outputs = []

# 建立兩個欄位
col1, col2 = st.columns([3, 1])

# **左邊欄位（col1）：顯示對話分析結果**
with col1:

    parsed_results = {}

    for output in st.session_state.outputs:
        component_id = output["component_id"]
        text_content = output["results"]["text"].get("text", "")
        timestamp = output["results"]["text"]["data"].get("timestamp", "1970-01-01 00:00:00 UTC")

        # **時區轉換（UTC +8）**
        try:
            dt_utc = datetime.strptime(timestamp.replace(" UTC", ""), "%Y-%m-%d %H:%M:%S")
            dt_taipei = dt_utc + timedelta(hours=8)
            formatted_timestamp = dt_taipei.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            formatted_timestamp = "格式錯誤"

        # **根據 component_id 存入對應內容**
        if component_id == "TextOutput-fTzY9":
            parsed_results["問題拆解"] = {"text": text_content, "timestamp": formatted_timestamp}
        elif component_id == "TextOutput-JHNPu":
            parsed_results["內容彙整"] = {"text": text_content, "timestamp": formatted_timestamp}

    # 顯示解析結果
    st.header("🛠️ 問題拆解")
    st.write(parsed_results.get("問題拆解", {}).get("timestamp", ""))
    st.write(parsed_results.get("問題拆解", {}).get("text", ""))

    st.header("📖 內容彙整")
    st.write(parsed_results.get("內容彙整", {}).get("timestamp", ""))
    st.write(parsed_results.get("內容彙整", {}).get("text", ""))

    # **輸入框固定在底部**
    with st.container():
        st.markdown("---")  # 分隔線
        user_input = st.text_area("輸入訊息後按 Enter 送出", key="user_input", placeholder="輸入你的訊息...")

        if st.button("送出"):
            if user_input.strip():  # 避免空白輸入
                st.session_state.latest_input = user_input  # 儲存輸入內容

                # 呼叫 Langchain API 進行對話摘要分析
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                data = {
                    "input_value": user_input,
                    "output_type": "text",
                    "input_type": "text",
                    "tweaks": {
                        "TextOutput-fTzY9": {"output_format": "json"},
                        "TextOutput-Mps7C": {"output_format": "json"},
                        "TextOutput-JHNPu": {"output_format": "json"}
                    }
                }

                # 發送請求
                response = requests.post(langchain_api_url, headers=headers, json=data)
                response.raise_for_status()  # 若發生錯誤會觸發例外
                st.session_state.outputs = response.json()["outputs"][0]["outputs"]

                # **清空輸入框並更新畫面**
                st.rerun()

# **右側欄位（col2）：資訊來源**
with col2:
    st.header("🔎 資訊來源")
    parsed_results = {}

    for output in st.session_state.outputs:
        component_id = output["component_id"]
        text_content = output["results"]["text"].get("text", "")
        timestamp = output["results"]["text"]["data"].get("timestamp", "1970-01-01 00:00:00 UTC")

        # **轉換時區**
        try:
            dt_utc = datetime.strptime(timestamp.replace(" UTC", ""), "%Y-%m-%d %H:%M:%S")
            dt_taipei = dt_utc + timedelta(hours=8)
            formatted_timestamp = dt_taipei.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            formatted_timestamp = "格式錯誤"

        if component_id == "TextOutput-Mps7C":
            parsed_results["資訊來源"] = {"text": text_content, "timestamp": formatted_timestamp}

    st.write(parsed_results.get("資訊來源", {}).get("timestamp", ""))
    
    # **預設顯示 200 字，可展開查看完整內容**
    content = parsed_results.get("資訊來源", {}).get("text", "")
    preview_text = content[:200]
    
    with st.expander(preview_text + ("..." if len(content) > 200 else "")):
        st.write(content)  # 展開後顯示完整訊息
