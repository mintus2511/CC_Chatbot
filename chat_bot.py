import pandas as pd
import streamlit as st 
import requests

# Streamlit UI
st.title("Call Center CHATBOT")

# GitHub API Setup
GITHUB_USER = "Menbeo"
GITHUB_REPO = "-HUHU-"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/"

def get_latest_csv():
    """Lấy file CSV mới nhất trong repo GitHub"""
    try:
        response = requests.get(GITHUB_API_URL)
        response.raise_for_status()
        files = response.json()

        # Lọc danh sách file CSV
        csv_files = [file for file in files if file["name"].endswith(".csv")]
        if not csv_files:
            st.warning("Không có file CSV nào trong repository.")
            return None, None

        # Sắp xếp theo thời gian cập nhật gần nhất (updated_at)
        csv_files = sorted(csv_files, key=lambda x: x.get("updated_at", ""), reverse=True)

        latest_csv = csv_files[0]  # Lấy file CSV mới nhất
        return latest_csv["name"], latest_csv["download_url"]

    except requests.exceptions.RequestException as e:
        st.error("Lỗi kết nối GitHub. Vui lòng kiểm tra lại.")
        return None, None

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

# Lấy file CSV mới nhất từ GitHub
latest_csv_name, latest_csv_url = get_latest_csv()
exist_program = load_data(latest_csv_url) if latest_csv_url else None

# Hiển thị dữ liệu
if exist_program is not None:
    st.success(f"Đang sử dụng file CSV: **{latest_csv_name}**")
    
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
