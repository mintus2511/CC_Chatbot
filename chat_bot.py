import pandas as pd
import streamlit as st
import requests

# Streamlit UI
st.title("Call Center CHATBOT")

# GitHub API Setup
GITHUB_USER = "Menbeo"
GITHUB_REPO = "-HUHU-"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/"

def get_csv_files():
    """Lấy danh sách tất cả file CSV trong repo GitHub"""
    try:
        response = requests.get(GITHUB_API_URL)
        response.raise_for_status()
        files = response.json()

        # Lọc danh sách file CSV
        csv_files = {file["name"]: file["download_url"] for file in files if file["name"].endswith(".csv")}
        
        if not csv_files:
            st.warning("Không có file CSV nào trong repository.")
        
        return csv_files
    except requests.exceptions.RequestException as e:
        st.error("Lỗi kết nối GitHub. Vui lòng kiểm tra lại.")
        return {}

def load_data(url):
    """Đọc dữ liệu CSV từ GitHub"""
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.lower().str.strip()  # Chuẩn hóa tên cột
        required_columns = {"key word", "description"}

        if not required_columns.issubset(df.columns):
            st.error(f"Thiếu cột bắt buộc: {required_columns - set(df.columns)}")
            return None

        return df
    except Exception:
        st.error(f"Lỗi tải file CSV từ {url}. Vui lòng kiểm tra lại.")
        return None

# Lấy danh sách file CSV từ GitHub
csv_files = get_csv_files()

# Cho phép người dùng chọn file CSV
if csv_files:
    selected_csv = st.selectbox("Chọn file CSV để sử dụng", list(csv_files.keys()))
    selected_csv_url = csv_files[selected_csv]
    exist_program = load_data(selected_csv_url)
else:
    exist_program = None

# Upload file mới từ người dùng
st.sidebar.header("Tải lên file CSV mới")
uploaded_file = st.sidebar.file_uploader("Chọn file CSV", type=["csv"])

if uploaded_file:
    try:
        new_data = pd.read_csv(uploaded_file)
        new_data.columns = new_data.columns.str.lower().str.strip()  # Chuẩn hóa tên cột
        required_columns = {"key word", "description"}

        if required_columns.issubset(new_data.columns):
            if exist_program is not None:
                exist_program = pd.concat([exist_program, new_data]).drop_duplicates().reset_index(drop=True)
            else:
                exist_program = new_data
            st.sidebar.success("Dữ liệu mới đã được cập nhật!")
        else:
            st.sidebar.error("File thiếu cột bắt buộc!")
    except Exception:
        st.sidebar.error("Lỗi đọc file. Hãy kiểm tra định dạng CSV.")

# Hiển thị dữ liệu
if exist_program is not None:
    st.success(f"Đang sử dụng file CSV: **{selected_csv}**")

    # Lớp chatbot xử lý dữ liệu
    class Data:
        def __init__(self, dataframe):
            self.dataframe = dataframe
            self.activate = dataframe['key word'].astype(str).tolist() if 'key word' in dataframe.columns else []

        def list_keywords(self):
            return self.activate

        def description(self, keyword):
            if keyword in self.activate:
                responses = self.dataframe.loc[self.dataframe['key word'] == keyword, 'description']
                return responses.iloc[0] if not responses.empty else "Không có mô tả."
            return "Không có dữ liệu. Nếu muốn thêm, hãy nhập 'add'."

    data = Data(exist_program)

    if data.list_keywords():
        select = st.selectbox("Chọn từ khóa", data.list_keywords())
        if select:
            bot_response = data.description(select)
            st.write("Bot:", bot_response)
    else:
        st.warning("Không có từ khóa nào trong file này.")
else:
    st.error("Không tìm thấy file CSV hợp lệ. Hãy kiểm tra GitHub repository.")
