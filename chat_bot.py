import pandas as pd
import streamlit as st
import requests

# Streamlit UI
st.title("Call Center CHATBOT")

# GitHub raw CSV file
GITHUB_USER = "mintus2511"
GITHUB_REPO = "CC_Chatbot"
CSV_FILE_NAME = "combined_data.csv"  # Your single CSV file
CSV_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/{CSV_FILE_NAME}"

@st.cache_data(ttl=60)
def load_csv_from_github(url):
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.lower().str.strip()
        if {"key word", "description"}.issubset(df.columns):
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Lỗi khi đọc CSV từ GitHub: {e}")
        return pd.DataFrame()

data = load_csv_from_github(CSV_URL)

if not data.empty:
    keywords = data["key word"].dropna().astype(str).unique().tolist()
    keyword_input = st.text_input("🔍 Nhập từ khóa", "", placeholder="Gõ từ khóa...", autocomplete=keywords)

    if keyword_input:
        matched = data[data["key word"].str.lower() == keyword_input.strip().lower()]
        if not matched.empty:
            description = matched["description"].iloc[0]
            source = matched["topic"].iloc[0] if "topic" in matched.columns else "không rõ"
            st.write("🤖 **Bot:**", description)
            st.caption(f"(Nguồn: `{source}`)")
        else:
            st.info("Không tìm thấy mô tả cho từ khóa này.")
else:
    st.error("⚠️ Không tìm thấy dữ liệu hợp lệ.")
