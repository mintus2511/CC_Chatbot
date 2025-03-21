import pandas as pd
import streamlit as st
import requests

# Streamlit UI
st.title("Call Center CHATBOT")

# GitHub API Setup
GITHUB_USER = "Menbeo"
GITHUB_REPO = "-HUHU-"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/"

def get_all_csv_files():
    """Lấy danh sách file CSV từ GitHub"""
    try:
        response = requests.get(GITHUB_API_URL)
        response.raise_for_status()
        files = response.json()

        return {file["name"]: file["download_url"] for file in files if file["name"].endswith(".csv")}
    except requests.exceptions.RequestException:
        return {}

def load_data(url):
    """Đọc dữ liệu từ URL (GitHub)"""
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.lower().str.strip()
        return df if {"key word", "description"}.issubset(df.columns) else None
    except Exception:
        return None

# Lấy danh sách file CSV từ GitHub
csv_files = get_all_csv_files()

# Lưu trữ danh sách tất cả CSV files từ GitHub
all_data = {}
for file_name, file_url in csv_files.items():
    new_data = load_data(file_url)
    if new_data is not None:
        all_data[file_name] = new_data

# Hiển thị dữ liệu
if all_data:
    st.success(f"Tìm thấy {len(all_data)} tập dữ liệu!")

    # Selectbox 1: Chọn file (topic)
    topic_choice = st.selectbox("Chọn chủ đề", [""] + list(all_data.keys()), index=0)

    if topic_choice:
        selected_df = all_data[topic_choice]
        keywords = selected_df["key word"].astype(str).tolist()

        # Selectbox 2: Chọn từ khóa trong file đã chọn
        keyword_choice = st.selectbox("Chọn từ khóa", [""] + keywords, index=0)

        if keyword_choice:
            description = selected_df.loc[selected_df["key word"] == keyword_choice, "description"]
            bot_response = description.iloc[0] if not description.empty else "Không có mô tả."
            st.write("Bot:", bot_response)
else:
    st.error("Không tìm thấy dữ liệu hợp lệ.")
