import streamlit as st
import requests
import json
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

# 讀取 .env 檔案中的環境變數
load_dotenv()

# 從環境變數讀取 Langchain API URL 和 API 金鑰
langchain_api_url = os.getenv("LANGCHAIN_API_URL")
api_key = os.getenv("API_KEY")



# 設定頁面標題
st.set_page_config(page_title="對話輸入介面", layout="wide")

# 使用 CSS 調整頁面寬度
st.markdown("""
    <style>
        /* 調整頁面整體內容的最大寬度 */
        .block-container {
            max-width: 90% !important;  /* 設定寬度為 90% */
            padding-left: 5% !important;
            padding-right: 5% !important;
        }
    </style>
""", unsafe_allow_html=True)

# 初始化對話歷史，只存一筆
if "latest_message" not in st.session_state:
    st.session_state.latest_message = {"role": "user", "content": ""}

# 創建左右兩個欄位
col1, col2 = st.columns([1, 2])


# **左側：對話輸入區**
with col1:

    st.header("💬 輸入對話")
    user_input = st.text_area("請輸入你的訊息：", key="user_input", height=150)

    if st.button("送出"):
        if user_input.strip():  # 避免空白輸入
             # **儲存最新的訊息，只保留一筆**
            st.session_state.latest_input = user_input  # 儲存輸入內容
            
            # 呼叫 Langchain API 進行對話摘要分析
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            # data = {
            #     "input_value": user_input
            # }


            data ={
                "input_value": user_input,
                "output_type": "text",
                "input_type": "text",
                "tweaks": {
                    "TextOutput-fTzY9": { "output_format": "json" },
                    "TextOutput-Mps7C": { "output_format": "json" },
                    "TextOutput-JHNPu": { "output_format": "json" }
                    }
            }


            # 發送 POST 請求給 Langchain API
            response = requests.post(langchain_api_url, headers=headers, json=data)
            response.raise_for_status()  # 若發生錯誤會觸發例外
            st.session_state.outputs=response.json()["outputs"][0]["outputs"]


            # **清空輸入框並更新畫面**
            st.rerun()


# **右側：顯示對話分析紀錄**

with col2:
    if "outputs" not in st.session_state:
        st.session_state.outputs = []

    outputs = st.session_state.outputs

    # **1️⃣ 解析 API 回應**
    parsed_results = {}

    for output in outputs:
        component_id = output["component_id"]
        text_content = output["results"]["text"].get("text", "")
        timestamp = output["results"]["text"]["data"].get("timestamp", "1970-01-01 00:00:00 UTC")

        # **格式化 timestamp 並轉換時區**
        try:
            # 去掉 " UTC"，轉換為 `datetime` 物件
            dt_utc = datetime.strptime(timestamp.replace(" UTC", ""), "%Y-%m-%d %H:%M:%S")
            # **時區轉換：從 UTC +8**
            dt_taipei = dt_utc + timedelta(hours=8)
            formatted_timestamp = dt_taipei.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            formatted_timestamp = "格式錯誤"

        # **根據 component_id 存入對應內容**
        if component_id == "TextOutput-fTzY9":
            parsed_results["問題拆解"] = {"text": text_content, "timestamp": formatted_timestamp}
        elif component_id == "TextOutput-Mps7C":
            parsed_results["資訊來源"] = {"text": text_content, "timestamp": formatted_timestamp}
        elif component_id == "TextOutput-JHNPu":
            parsed_results["內容彙整"] = {"text": text_content, "timestamp": formatted_timestamp}

    # **2️⃣ 輸出解析結果**
    st.header("🛠️ 問題拆解")
    st.write(parsed_results.get("問題拆解", {}).get("timestamp", ""))
    st.write(parsed_results.get("問題拆解", {}).get("text", ""))


    st.header("🔎 資訊來源")
    st.write(parsed_results.get("資訊來源", {}).get("timestamp", ""))
    st.write(parsed_results.get("資訊來源", {}).get("text", ""))

    st.header("📖 內容彙整")
    st.write(parsed_results.get("內容彙整", {}).get("timestamp", ""))
    st.write(parsed_results.get("內容彙整", {}).get("text", ""))
