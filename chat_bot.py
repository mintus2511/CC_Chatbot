import pandas as pd
import streamlit as st
import requests
from streamlit_searchbox import st_searchbox

# === Streamlit Title ===
st.title("📞 Call Center Chatbot")

# === GitHub Setup ===
GITHUB_USER = "mintus2511"
GITHUB_REPO = "CC_Chatbot"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/"

# === Cache GitHub CSV Links ===
@st.cache_data(ttl=60)
def get_csv_file_links():
    try:
        response = requests.get(GITHUB_API_URL)
        response.raise_for_status()
        files = response.json()
        return {
            file["name"]: file["download_url"]
            for file in files if file["name"].endswith(".csv")
        }
    except Exception as e:
        st.error(f"❌ Lỗi khi kết nối tới GitHub: {e}")
        return {}

# === Cache Merged CSV Data ===
@st.cache_data(ttl=60)
def load_csvs(csv_files):
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

# === Load CSVs from GitHub ===
csv_files = get_csv_file_links()
data = load_csvs(csv_files)

# === Chatbot Autocomplete UI ===
if not data.empty:
    all_keywords = sorted(data["key word"].dropna().astype(str).unique())

    def search_fn(user_input):
        return [kw for kw in all_keywords if user_input.lower() in kw.lower()]

    # Use session_state to avoid rerunning on every key press
    selected_keyword = st_searchbox(
        search_fn,
        key="keyword_search",
        label="🔍 Gõ từ khóa",
        placeholder="Ví dụ: học phí, quy trình tuyển sinh, thời gian tuyển sinh,...",
    )

    # Store selected keyword in session
    if selected_keyword:
        st.session_state["selected_keyword"] = selected_keyword

    # Trigger search only if a keyword is selected
    if "selected_keyword" in st.session_state:
        keyword = st.session_state["selected_keyword"]
        matches = data[data["key word"].str.lower().str.contains(keyword.lower(), na=False)]

        if not matches.empty:
            for _, row in matches.iterrows():
                st.write("🤖 **Bot:**", row["description"])
                st.caption(f"(📂 Chủ đề: `{row['topic']}` | 🔑 Từ khóa: `{row['key word']}`)")
        else:
            st.info("Không tìm thấy mô tả cho từ khóa này.")
else:
    st.error("⚠️ Không tìm thấy dữ liệu hợp lệ.")

