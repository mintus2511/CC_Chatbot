import pandas as pd
import streamlit as st
import requests
from streamlit_searchbox import st_searchbox

# === Streamlit App Title ===
st.title("Call Center Chatbot")

# === GitHub Repo Info ===
GITHUB_USER = "mintus2511"
GITHUB_REPO = "CC_Chatbot"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/"

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

# === Load Data ===
csv_files = get_csv_file_links()
data = load_csvs(csv_files)

# === UI with Autocomplete + Partial Matching ===
if not data.empty:
    all_keywords = sorted(data["key word"].dropna().astype(str).unique())

    def search_fn(user_input):
        return [kw for kw in all_keywords if user_input.lower() in kw.lower()]

    selected_keyword = st_searchbox(
        search_fn,
        placeholder="🔍 Gõ từ khóa...",
        label="Từ khóa",
        key="keyword_autocomplete"
    )

# Search all partial matches (only if something was selected/typed)
if selected_keyword:
    matches = data[data["key word"].str.lower().str.contains(selected_keyword.lower(), na=False)]
    if not matches.empty:
        for _, row in matches.iterrows():
            st.write("🤖 **Bot:**", row["description"])
            st.caption(f"(📂 Chủ đề: `{row['topic']}` | 🔑 Từ khóa: `{row['key word']}`)")
    else:
        st.info("Không tìm thấy mô tả cho từ khóa này.")
