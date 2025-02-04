import streamlit as st
from transformers import pipeline

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

# **初始化情緒分析模型**
sentiment_analyzer = pipeline("sentiment-analysis", model="uer/roberta-base-finetuned-jd-binary-chinese")

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

            # **執行情緒分析**
            sentiment_result = sentiment_analyzer(user_input)
            st.session_state.sentiment = sentiment_result[0]  # 只取第一個分析結果
            
            # **清空輸入框並更新畫面**
            st.rerun()  

# **右側：顯示對話分析紀錄**
with col2:

    st.header("📜 對話分析")
    
    # 讀取最新輸入的字數
    latest_text = st.session_state.get("latest_input", "")
    word_count = len(latest_text.strip())  # 計算字數（去掉前後空白）

    # st.write(f"輸入內容:{latest_text}")
    st.write(f"輸入字數 **{word_count}** 個字")

    if "sentiment" in st.session_state:
        sentiment = st.session_state.sentiment
        st.write(f"**情緒分析結果**: {sentiment['label']} (信心指數: {sentiment['score']:.2f})")


