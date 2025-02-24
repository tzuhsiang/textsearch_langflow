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

# 使用 CSS 調整頁面寬度與固定大小的顯示區
st.markdown("""
    <style>
        .block-container {
            max-width: 90% !important;  
            padding-left: 5% !important;
            padding-right: 5% !important;
        }
        
        /* 固定內容彙整區大小 */
        .fixed-size-container {
            height: 350px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 10px;
            white-space: pre-wrap;
            font-family: sans-serif;
        }
    </style>
""", unsafe_allow_html=True)

# 初始化 session_state
if "outputs" not in st.session_state:
    st.session_state.outputs = []
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# 時區轉換函數
def convert_timestamp(timestamp):
    try:
        dt_utc = datetime.strptime(timestamp.replace(" UTC", ""), "%Y-%m-%d %H:%M:%S")
        dt_taipei = dt_utc + timedelta(hours=8)
        return dt_taipei.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return "格式錯誤"

# 建立兩個欄位
col1, col2 = st.columns([3, 1])

# **左邊欄位（col1）：顯示對話分析結果**
with col1:
    parsed_results = {}

    for output in st.session_state.outputs:
        component_id = output["component_id"]
        text_content = output["results"]["text"].get("text", "")
        timestamp = output["results"]["text"]["data"].get("timestamp", "1970-01-01 00:00:00 UTC")
        formatted_timestamp = convert_timestamp(timestamp)

        # **根據 component_id 存入對應內容**
        if component_id == "TextOutput-fTzY9":
            parsed_results["問題拆解"] = {"text": text_content, "timestamp": formatted_timestamp}
        elif component_id == "TextOutput-JHNPu":
            parsed_results["內容彙整"] = {"text": text_content, "timestamp": formatted_timestamp}

    # **顯示對話分析結果**
    st.header("🛠️ 問題拆解")
    st.write(parsed_results.get("問題拆解", {}).get("timestamp", ""))
    st.write(parsed_results.get("問題拆解", {}).get("text", ""))

    st.header("📖 內容彙整")
    st.write(parsed_results.get("內容彙整", {}).get("timestamp", ""))
    st.markdown('<div class="fixed-size-container">'
     + parsed_results.get("內容彙整", {}).get("text", "") 
     + '</div>', unsafe_allow_html=True)



    # **快速輸入按鈕 (在同一水平列靠左)**
    button_container = st.container()
    with button_container:
        col_buttons = st.columns([1, 1, 1, 7])  # 三個按鈕靠左，右側留空間
        with col_buttons[0]:
            if st.button("今日新聞"):
                st.session_state.user_input = "今日台灣股市新聞"
        with col_buttons[1]:
            if st.button("美食推薦"):
                st.session_state.user_input = "推薦台北的炸雞店"
        with col_buttons[2]:
            if st.button("最近趨勢"):
                st.session_state.user_input = "最近AI的發展趨勢"

    # **輸入框**
    user_input = st.text_area("輸入訊息後按 Enter 送出", key="user_input", value=st.session_state.user_input, placeholder="輸入你的訊息...")
    
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
        formatted_timestamp = convert_timestamp(timestamp)

        if component_id == "TextOutput-Mps7C":
            parsed_results["資訊來源"] = {"text": text_content, "timestamp": formatted_timestamp}

    st.write(parsed_results.get("資訊來源", {}).get("timestamp", ""))
    
    content = parsed_results.get("資訊來源", {}).get("text", "")
    preview_text = content[:200]
    
    with st.expander(preview_text + ("..." if len(content) > 200 else "")):
        st.write(content)
