import pandas as pd
import streamlit as st
import requests
from streamlit_searchbox import st_searchbox

# === App Title ===
st.set_page_config(page_title="Call Center Chatbot", layout="wide")
st.title("📞 Call Center Chatbot")

# === Session state setup ===
if "selected_keyword" not in st.session_state:
    st.session_state["selected_keyword"] = None
if "pinned_keywords" not in st.session_state:
    st.session_state["pinned_keywords"] = []
if "multi_filter_keywords" not in st.session_state:
    st.session_state["multi_filter_keywords"] = []
if "selected_topics" not in st.session_state:
    st.session_state["selected_topics"] = []
if "trigger_display" not in st.session_state:
    st.session_state["trigger_display"] = False

# === User Guide ===
with st.expander("ℹ️ Hướng dẫn sử dụng chatbot", expanded=False):
    st.info("""
    **📘 Call Center Chatbot - Hướng Dẫn Sử Dụng**

    **1. Gõ hoặc chọn từ khóa**  
    🔍 Bạn có thể gõ từ khóa, lọc nhiều từ hoặc nhấn từ khóa đã ghim ở thanh bên trái để xem mô tả.

    **2. Dữ liệu tự động cập nhật**  
    📂 Dữ liệu được lấy từ GitHub và làm sạch trước khi hiển thị.
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
    combined = combined.drop_duplicates(subset="description", keep="first")

    return combined

# === Step 3: Load data ===
csv_files = get_csv_file_links()
data = load_csvs(csv_files)

# === Step 4: Setup helper ===
def set_selected_keyword(keyword):
    st.session_state["selected_keyword"] = keyword
    st.session_state["trigger_display"] = True

# === Step 5: UI and logic ===
if not data.empty:
    all_keywords = sorted(data["key word"].dropna().astype(str).unique())
    all_topics = sorted(data["topic"].dropna().unique())

    with st.sidebar:
        # === Lọc theo chủ đề ===
        st.markdown("### 🧭 Lọc theo chủ đề")
        selected_topics = st.multiselect("Chọn chủ đề:", all_topics)
        st.session_state["selected_topics"] = selected_topics

        # === Ghim từ khóa theo nhóm ===
        if st.session_state["pinned_keywords"]:
            st.markdown("### 📌 Từ khóa đã ghim")
            pinned_df = data[data["key word"].isin(st.session_state["pinned_keywords"])]
            for topic in sorted(pinned_df["topic"].unique()):
                with st.expander(f"📁 {topic}", expanded=False):
                    for kw in sorted(pinned_df[pinned_df["topic"] == topic]["key word"].unique()):
                        if st.button(f"📍 {kw}", key=f"pinned-{kw}"):
                            set_selected_keyword(kw)
                            st.rerun()

        # === Bộ lọc nhiều từ khóa ===
        st.markdown("### 🧠 Lọc nhiều từ khóa")
        filtered_keywords = data[data["topic"].isin(selected_topics)]["key word"].unique() if selected_topics else all_keywords
        selected_multi = st.multiselect("Chọn nhiều từ khóa:", sorted(filtered_keywords))
        st.session_state["multi_filter_keywords"] = selected_multi

        # === Danh sách từ khóa hiển thị trực tiếp ===
        st.markdown("### 📚 Danh mục từ khóa")
        topics_to_show = selected_topics if selected_topics else all_topics
        for topic in topics_to_show:
            st.markdown(f"**📁 {topic}**")
            topic_data = data[data["topic"] == topic]
            topic_keywords = sorted(topic_data["key word"].dropna().astype(str).unique())
            for kw in topic_keywords:
                cols = st.columns([0.8, 0.2])
                if cols[0].button(f"🔑 {kw}", key=f"kw-{topic}-{kw}"):
                    set_selected_keyword(kw)
                    st.rerun()
                pin_icon = "📌" if kw in st.session_state["pinned_keywords"] else "☆"
                if cols[1].button(pin_icon, key=f"pin-{topic}-{kw}"):
                    if kw in st.session_state["pinned_keywords"]:
                        st.session_state["pinned_keywords"].remove(kw)
                    else:
                        st.session_state["pinned_keywords"].insert(0, kw)
                    # ⚡ Cải thiện hiệu suất: không cần st.rerun() ở đây

    # === Search box ===
    def search_fn(user_input):
        return [kw for kw in all_keywords if user_input.lower() in kw.lower()]

    selected_keyword = st_searchbox(
        search_fn,
        key="keyword_search",
        label="🔍 Gõ từ khóa để tìm nhanh",
        placeholder="Ví dụ: học phí, học bổng..."
    )
    if selected_keyword:
        set_selected_keyword(selected_keyword)

    # === Hiển thị kết quả ===
    if st.session_state["multi_filter_keywords"]:
        st.subheader("📋 Kết quả theo nhiều từ khóa:")
        for kw in st.session_state["multi_filter_keywords"]:
            matches = data[data["key word"].str.lower().str.contains(kw.lower(), na=False)]
            for _, row in matches.iterrows():
                st.write(f"🤖 **{kw}**: {row['description']}")
    elif st.session_state["selected_keyword"] and st.session_state["trigger_display"]:
        st.session_state["trigger_display"] = False
        kw = st.session_state["selected_keyword"]
        matches = data[data["key word"].str.lower().str.contains(kw.lower(), na=False)]
        if not matches.empty:
            for _, row in matches.iterrows():
                st.write("🤖 **Bot:**", row["description"])
        else:
            st.info("⚠️ Không tìm thấy mô tả cho từ khóa này.")
else:
    st.error("⚠️ Không tìm thấy dữ liệu hợp lệ.")
