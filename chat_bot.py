import pandas as pd
import streamlit as st
import requests
from io import BytesIO

# Streamlit UI
st.title("Call Center CHATBOT")

# GitHub API Setup
GITHUB_USER = "mintus2511"
GITHUB_REPO = "CC_Chatbot"
EXCEL_FILE_NAME = "all_data.xlsx"  # Make sure your Excel file is named this
GITHUB_EXCEL_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/{EXCEL_FILE_NAME}"

@st.cache_data(ttl=60)
def load_excel_from_github(url):
    """Tải Excel từ GitHub và đọc tất cả các sheet"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        excel_file = BytesIO(response.content)

        # Đọc tất cả sheets
        all_sheets = pd.read_excel(excel_file, sheet_name=None)

        combined_data = pd.DataFrame(columns=["key word", "description"])
        for sheet_name, df in all_sheets.items():
            df.columns = df.columns.str.lower().str.strip()
            if {"key word", "description"}.issubset(df.columns):
                df["source"] = sheet_name  # optional: lưu tên sheet gốc
                combined_data = pd.concat([combined_data, df[["key word", "description", "source"]]], ignore_index=True)
        return combined_data
    except Exception as e:
        st.error(f"Lỗi khi đọc Excel từ GitHub: {e}")
        return pd.DataFrame()

# Load data
merged_data = load_excel_from_github(GITHUB_EXCEL_URL)

# User interaction
if not merged_data.empty:
    keyword_list = merged_data["key word"].dropna().astype(str).unique().tolist()
    keyword_input = st.text_input("🔍 Nhập từ khóa", "", placeholder="Gõ từ khóa...", autocomplete=keyword_list)

    if keyword_input:
        matched = merged_data[merged_data["key word"].str.lower() == keyword_input.strip().lower()]
        if not matched.empty:
            description = matched["description"].iloc[0]
            source = matched["source"].iloc[0]
            st.write("🤖 **Bot:**", description)
            st.caption(f"(Nguồn: Sheet `{source}`)")
        else:
            st.info("Không tìm thấy mô tả cho từ khóa này.")
else:
    st.error("⚠️ Không tìm thấy dữ liệu hợp lệ từ Excel.")
