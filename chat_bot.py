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
    "ASA_Work": "ASA_Work.csv",
    "Admissions": "Admissions.csv",
    "CC_Script": "CC_Script.csv",
    "Curriculum": "Curriculum.csv",
    "Hard_Questions": "Hard_Questions.csv",
    "Majors": "Majors.csv",
    "Offline_Event": "Offline_Event.csv",
    "OtherQuestions": "OtherQuestions.csv",
    "Scholarships": "Scholarships.csv",
    "Tuition": "Tuition.csv"
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

def get_all_csv_files():
    """Lấy danh sách tất cả file CSV trong repo GitHub"""
    try:
        response = requests.get(GITHUB_API_URL)
        response.raise_for_status()
        files = response.json()

        # Lọc danh sách file CSV
        csv_files = {file["name"]: file["download_url"] for file in files if file["name"].endswith(".csv")}

        if not csv_files:
            return {}

        return csv_files
    except requests.exceptions.RequestException:
        return {}

def load_data(url):
    """Đọc dữ liệu CSV từ GitHub"""
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.lower().str.strip()
        return df if {"key word", "description"}.issubset(df.columns) else None
    except Exception:
        return None

# Lấy dữ liệu cũ
all_data = load_old_data()

# Lấy danh sách file CSV từ GitHub
csv_files = get_all_csv_files()

# Thêm dữ liệu từ GitHub vào danh sách chọn
for file_name, file_url in csv_files.items():
    new_data = load_data(file_url)
    if new_data is not None:
        all_data[file_name] = new_data

# Sidebar: Upload file mới từ người dùng
st.sidebar.header("Tải lên file CSV mới")
uploaded_file = st.sidebar.file_uploader("Chọn file CSV", type=["csv"])

if uploaded_file:
    try:
        user_df = pd.read_csv(uploaded_file)
        user_df.columns = user_df.columns.str.lower().str.strip()  # Chuẩn hóa tên cột

        if {"key word", "description"}.issubset(user_df.columns):
            file_name = uploaded_file.name
            all_data[file_name] = user_df  # Thêm vào danh sách lựa chọn
            st.sidebar.success(f"File `{file_name}` đã được thêm vào danh sách!")
        else:
            st.sidebar.error("File thiếu cột bắt buộc!")
    except Exception:
        st.sidebar.error("Lỗi đọc file. Hãy kiểm tra định dạng CSV.")

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
