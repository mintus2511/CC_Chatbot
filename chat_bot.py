import pandas as pd
import streamlit as st
import requests
from streamlit_searchbox import st_searchbox

# === App Title ===
st.title("📞 Call Center Chatbot")

# === User Guide ===
with st.expander("ℹ️ Hướng dẫn sử dụng chatbot", expanded=False):
    st.info("""
    **📘 Call Center Chatbot - Hướng Dẫn Sử Dụng**

    **1. Gõ từ khóa**  
    🔍 Hoặc chọn từ khóa trực tiếp trong thanh bên trái để xem mô tả.

    **2. Dữ liệu tự động cập nhật**  
    📂 Dữ liệu được lấy từ GitHub và làm sạch trước khi hiển thị.

    **🛠 Góp ý & Báo lỗi**  
    Vui lòng liên hệ nhóm phát triển tại: [GitHub Repo](https://github.com/Menbeo/-HUHU-)
    """)

# === GitHub Repo Info ===
GITHUB_USER = "mintus2511"
GITHUB_REPO = "CC_Chatbot"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/"

# === Step 1: Get CSV files from GitHub ===
@st.cache_data(ttl=60)
def get_csv_file_links():
    try:
        response = requests.get(GITHUB_API_URL)
        response.raise_for_status()
        files = response.json()

        sorted_csvs = sorted(
            [file for file in files if file["name"].endswith(".csv")],
            key=lambda x: x["name"]
        )

        return {
            file["name"]: file["download_url"]
            for file in sorted_csvs
        }
    except Exception as e:
        st.error(f"❌ Lỗi khi kết nối tới GitHub: {e}")
        return {}

# === Step 2: Load & clean CSVs ===
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

    combined = combined.drop_duplicates(subset="key word", keep="last")
    dupes = combined[combined.duplicated("description", keep=False)].copy()
    removed_duplicates = dupes[dupes.duplicated("description", keep="first")]
    cleaned_data = combined.drop_duplicates(subset="description", keep="first")

    return cleaned_data, removed_duplicates

# === Step 3: Load data ===
csv_files = get_csv_file_links()
data, removed_duplicates = load_csvs(csv_files)

# === Step 4: UI & Logic ===
if not data.empty:
    all_keywords = sorted(data["key word"].dropna().astype(str).unique())
    all_topics = sorted(data["topic"].dropna().unique())

    # === Sidebar: Interactive keyword buttons grouped by topic ===
    with st.sidebar:
        st.markdown("## 📚 Danh mục từ khóa")
        st.markdown("Nhấn vào từ khóa để xem câu trả lời tương ứng.")

        for topic in all_topics:
            with st.expander(f"📁 {topic}", expanded=False):
                topic_data = data[data["topic"] == topic]
                topic_keywords = sorted(topic_data["key word"].dropna().astype(str).unique())
                for kw in topic_keywords:
                    if st.button(f"🔑 {kw}", key=f"{topic}-{kw}"):
                        st.session_state["selected_keyword"] = kw

    # === Main search box (optional) ===
    def search_fn(user_input):
        return [kw for kw in all_keywords if user_input.lower() in kw.lower()]

    selected_keyword = st_searchbox(
        search_fn,
        key="keyword_search",
        label="🔍 Gõ từ khóa để tìm nhanh",
        placeholder="Ví dụ: học phí, học bổng..."
    )

    if selected_keyword:
        st.session_state["selected_keyword"] = selected_keyword

    # === Main Output: Bot Answer ===
    if "selected_keyword" in st.session_state:
        keyword = st.session_state["selected_keyword"]
        matches = data[data["key word"].str.lower().str.contains(keyword.lower(), na=False)]

        if not matches.empty:
            st.subheader(f"Kết quả cho từ khóa: `{keyword}`")
            for _, row in matches.iterrows():
                st.write("🤖 **Bot:**", row["description"])
        else:
            st.info("Không tìm thấy mô tả cho từ khóa này.")
else:
    st.error("⚠️ Không tìm thấy dữ liệu hợp lệ.")
