import pandas as pd
import streamlit as st 
import requests

# Streamlit UI
st.title("Call Center CHATBOT")

# GitHub API Setup
GITHUB_USER = "Menbeo"
GITHUB_REPO = "-HUHU-"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/"

# Danh sách file dữ liệu cũ
old_files = [
    r"D:\WORK-PROJECT\data\cc - Trang tính1.csv",
    r"D:\WORK-PROJECT\data\program  - Trang tính1.csv",
    r"D:\WORK-PROJECT\data\other  - Trang tính1.csv",
    r"D:\WORK-PROJECT\data\ts  - Trang tính1.csv",
    r"D:\WORK-PROJECT\data\hard - Trang tính1.csv",
    r"D:\WORK-PROJECT\data\hb - Trang tính1.csv",
    r"D:\WORK-PROJECT\data\major  - Trang tính1.csv"
]

def load_old_data():
    """Đọc và gộp dữ liệu từ các file cũ."""
    try:
        df_list = [pd.read_csv(file) for file in old_files]
        old_data = pd.concat(df_list, ignore_index=True).drop_duplicates()
        return old_data
    except Exception as e:
        st.error(f"Lỗi đọc dữ liệu cũ: {e}")
        return None

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

        # Sắp xếp theo thời gian cập nhật gần nhất
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

# Lấy dữ liệu cũ
old_data = load_old_data()

# Lấy file CSV mới nhất từ GitHub
latest_csv_name, latest_csv_url = get_latest_csv()
new_data = load_data(latest_csv_url) if latest_csv_url else None

# Hợp nhất dữ liệu cũ và GitHub
dataframes = [df for df in [old_data, new_data] if df is not None]
if dataframes:
    merged_data = pd.concat(dataframes, ignore_index=True).drop_duplicates()
else:
    merged_data = None

# Hiển thị dữ liệu cuối cùng
if merged_data is not None:
    st.success(f"Dữ liệu được tổng hợp từ {len(dataframes)} nguồn!")
    
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

    data = Data(merged_data)

    if data.list_keywords():
        # Hiển thị tất cả từ khóa trong select box
        select = st.selectbox("Chọn từ khóa", [""] + data.list_keywords(), index=0)
        
        if select:
            bot_response = data.description(select)
            st.write("Bot:", bot_response)
    else:
        st.warning("Không có từ khóa nào trong dữ liệu.")
else:
    st.error("Không tìm thấy dữ liệu hợp lệ.")
