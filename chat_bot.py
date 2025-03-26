import pandas as pd
import streamlit as st
import requests
from difflib import get_close_matches

# Streamlit UI
st.title("📞 Call Center Chatbot with Autocomplete")

# GitHub repo setup
GITHUB_USER = "mintus2511"
GITHUB_REPO = "CC_Chatbot"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/"

@st.cache_data(ttl=60)
def get_csv_file_links():
    """Get all CSV file names and download URLs from GitHub repo"""
    try:
        response = requests.get(GITHUB_API_URL)
        response.raise_for_status()
        files = response.json()
        return {
            file["name"]: file["download_url"]
            for file in files if file["name"].endswith(".csv")
        }
    except Exception as e:
        st.error(f"Lỗi khi kết nối tới GitHub: {e}")
        return {}

def load_csvs(csv_files):
    """Load and combine all valid CSVs"""
    combined = pd.DataFrame(columns=["key word", "description", "topic"])

    for name, url in csv_files.items():
        try:
            df = pd.read_csv(url)
            df.columns = df.columns.str.lower().str.strip()

            if {"key word", "description"}.issubset(df.columns):
                df["topic"] = name.replace(".csv", "")
                combined = pd.concat([combined, df[["key word", "description", "topic"]]], ignore_index=True)
        except Exception as e:
            st.warning(f"⚠️ Lỗi đọc {name}: {e}")
    
    return combined

# Load data
csv_files = get_csv_file_links()
data = load_csvs(csv_files)

# UI: Autocomplete-style interaction
if not data.empty:
    all_keywords = sorted(data["key word"].dropna().astype(str).unique().tolist())
    user_input = st.text_input("🔍 Gõ từ khóa (bot sẽ gợi ý khi bạn nhập)...", "")

    suggestions = get_close_matches(user_input, all_keywords, n=5, cutoff=0.3) if user_input else []

    if suggestions:
        suggestion_choice = st.selectbox("🔎 Có phải bạn muốn hỏi về:", suggestions)
        selected_keyword = suggestion_choice
    else:
        selected_keyword = user_input

    if selected_keyword:
        matches = data[data["key word"].str.lower() == selected_keyword.lower()]
        if not matches.empty:
            for _, row in matches.iterrows():
                st.write("🤖 **Bot:**", row["description"])
                st.caption(f"(📂 Từ chủ đề: `{row['topic']}`)")
        else:
            st.info("Không tìm thấy mô tả cho từ khóa này.")
else:
    st.error("⚠️ Không tìm thấy dữ liệu hợp lệ.")
