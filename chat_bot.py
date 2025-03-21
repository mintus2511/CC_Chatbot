import pandas as pd
import streamlit as st
import requests

# Streamlit UI
st.title("Call Center CHATBOT")

# GitHub API Setup
GITHUB_USER = "Menbeo"
GITHUB_REPO = "-HUHU-"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/"

@st.cache_data(ttl=60)  # Cache data for 60 seconds to reduce API calls
def get_all_csv_files():
    """Lấy danh sách tất cả file CSV từ GitHub"""
    try:
        response = requests.get(GITHUB_API_URL)
        response.raise_for_status()
        files = response.json()

        # Lọc các file có đuôi .csv
        csv_files = {file["name"]: file["download_url"] for file in files if file["name"].endswith(".csv")}
        return csv_files
    except requests.exceptions.RequestException as e:
        st.error(f"Lỗi khi kết nối GitHub: {e}")
        return {}

def load_data(url):
    """Đọc dữ liệu từ URL (GitHub)"""
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.lower().str.strip()

        # Kiểm tra cột bắt buộc
        if {"key word", "description"}.issubset(df.columns):
            return df
        else:
            st.warning(f"⚠️ File {url} thiếu cột bắt buộc!")
            return None
    except Exception as e:
        st.warning(f"⚠️ Lỗi đọc file {url}: {e}")
        return None

# Lấy danh sách tất cả CSV files từ GitHub
csv_files = get_all_csv_files()

# Lưu trữ tất cả dữ liệu từ GitHub
all_data = {}
for file_name, file_url in csv_files.items():
    new_data = load_data(file_url)
    if new_data is not None:
        all_data[file_name] = new_data

# Hiển thị dữ liệu nếu có ít nhất 1 file hợp lệ
if all_data:
    #st.success(f"📂 Đã tìm thấy {len(all_data)} tập dữ liệu hợp lệ!")

    # Chọn chủ đề (file CSV)
    topic_choice = st.selectbox("📌 Chọn chủ đề", [""] + list(all_data.keys()), index=0)

    if topic_choice:
        selected_df = all_data[topic_choice]
        keywords = selected_df["key word"].astype(str).tolist()

        # Chọn từ khóa trong file đã chọn
        keyword_choice = st.selectbox("🔍 Chọn từ khóa", [""] + keywords, index=0)

        if keyword_choice:
            description = selected_df.loc[selected_df["key word"] == keyword_choice, "description"]
            bot_response = description.iloc[0] if not description.empty else "Không có mô tả."
            st.write("🤖 **Bot:**", bot_response)
else:
    st.error("⚠️ Không tìm thấy dữ liệu hợp lệ. Kiểm tra GitHub repository.")
