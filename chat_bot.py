import pandas as pd
import streamlit as st 
import requests

# Streamlit UI
st.title("Call Center CHATBOT")

# GitHub API Setup
GITHUB_USER = "Menbeo"
GITHUB_REPO = "-HUHU-"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/"

# Danh sách file dữ liệu cũ (đã đổi tên theo yêu cầu)
file_mapping = {
    "ASA_Work": r"ASA_Work.csv",
    "Admissions": r"Admissions.csv",
    "CC_Script": r"CC_Script.csv",
    "Curriculum": r"Curriculum.csv",
    "Hard_Questions": r"Hard_Questions.csv",
    "Majors": r"Majors.csv",
    "Offline_Event": r"Offline_Event.csv",
    "OtherQuestions": r"OtherQuestions.csv",
    "Scholarships": r"Scholarships.csv",
    "Tuition": r"Tuition.csv"
}

def load_old_data():
    """Đọc tất cả dữ liệu từ file cũ và lưu theo từng topic"""
    data = {}
    for topic, path in file_mapping.items():
        try:
            df = pd.read_csv(path)
            df.columns = df.columns.str.lower().str.strip()  # Chuẩn hóa tên cột
            if {"key word", "description"}.issubset(df.columns):
                data[topic] = df
        except Exception as e:
            st.warning(f"Không thể đọc {topic}: {e}")
    return data

def get_latest_csv():
    """Lấy file CSV mới nhất trong repo GitHub"""
    try:
        response = requests.get(GITHUB_API_URL)
        response.raise_for_status()
        files = response.json()

        # Lọc danh sách file CSV
        csv_files = [file for file in files if file["name"].endswith(".csv")]
        if not csv_files:
            return None, None

        # Sắp xếp theo thời gian cập nhật gần nhất
        csv_files = sorted(csv_files, key=lambda x: x.get("updated_at", ""), reverse=True)
        latest_csv = csv_files[0]
        return latest_csv["name"], latest_csv["download_url"]

    except requests.exceptions.RequestException:
        return None, None

def load_data(url):
    """Đọc dữ liệu CSV từ GitHub"""
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.lower().str.strip()
        return df if {"key word", "description"}.issubset(df.columns) else None
    except Exception:
        return None

# Lấy dữ liệu cũ
old_data = load_old_data()

# Lấy file CSV mới nhất từ GitHub
latest_csv_name, latest_csv_url = get_latest_csv()
new_data = load_data(latest_csv_url) if latest_csv_url else None

# Gộp dữ liệu mới từ GitHub nếu có
if new_data is not None:
    old_data[latest_csv_name] = new_data  # Thêm dữ liệu GitHub vào danh sách

# Hiển thị dữ liệu
if old_data:
    st.success(f"Tìm thấy {len(old_data)} tập dữ liệu!")

    # Selectbox 1: Chọn file (topic)
    topic_choice = st.selectbox("Chọn chủ đề", [""] + list(old_data.keys()), index=0)

    if topic_choice:
        selected_df = old_data[topic_choice]
        keywords = selected_df["key word"].astype(str).tolist()

        # Selectbox 2: Chọn từ khóa trong file đã chọn
        keyword_choice = st.selectbox("Chọn từ khóa", [""] + keywords, index=0)

        if keyword_choice:
            description = selected_df.loc[selected_df["key word"] == keyword_choice, "description"]
            bot_response = description.iloc[0] if not description.empty else "Không có mô tả."
            st.write("Bot:", bot_response)
else:
    st.error("Không tìm thấy dữ liệu hợp lệ.")
