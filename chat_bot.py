import pandas as pd
import streamlit as st
import requests

# Streamlit UI
st.title("Call Center CHATBOT")

# GitHub API Setup
GITHUB_USER = "mintus2511"
GITHUB_REPO = "CC_Chatbot"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/"

@st.cache_data(ttl=60)
def get_all_csv_files():
    """Lấy danh sách tất cả file CSV từ GitHub"""
    try:
        response = requests.get(GITHUB_API_URL)
        response.raise_for_status()
        files = response.json()

        # Lọc các file .csv và tạo dict {filename: download_url}
        return {
            file["name"]: file["download_url"]
            for file in files
            if file["name"].endswith(".csv")
        }
    except requests.exceptions.RequestException as e:
        st.error(f"Lỗi khi kết nối GitHub: {e}")
        return {}

def load_and_combine_csvs(csv_files):
    """Tải và hợp nhất tất cả CSV thành một DataFrame"""
    combined_data = pd.DataFrame(columns=["key word", "description", "topic"])

    for file_name, file_url in csv_files.items():
        try:
            df = pd.read_csv(file_url)
            df.columns = df.columns.str.lower().str.strip()
            
            if {"key word", "description"}.issubset(df.columns):
                df = df[["key word", "description"]].copy()
                df["topic"] = file_name.replace(".csv", "")  # Add topic from filename
                combined_data = pd.concat([combined_data, df], ignore_index=True)
        except Exception as e:
            st.warning(f"⚠️ Không thể đọc {file_name}: {e}")
    
    return combined_data

# Load and merge all CSVs
csv_files = get_all_csv_files()
merged_data = load_and_combine_csvs(csv_files)

# UI: Chatbot Interaction
if not merged_data.empty:
    keyword_input = st.text_input("🔍 Nhập từ khóa", placeholder="Gõ từ khóa...").strip().lower()

    if keyword_input:
        matched = merged_data[merged_data["key word"].str.lower() == keyword_input]
        if not matched.empty:
            for _, row in matched.iterrows():
                st.write("🤖 **Bot:**", row["description"])
                st.caption(f"(📂 Từ chủ đề: `{row['topic']}`)")
        else:
            st.info("Không tìm thấy mô tả cho từ khóa này.")
else:
    st.error("⚠️ Không tìm thấy dữ liệu hợp lệ.")
