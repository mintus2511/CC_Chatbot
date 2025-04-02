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

    **1. Nhập từ khóa**  
    🔍 Gõ từ khóa vào ô tìm kiếm (ví dụ: *học phí, học bổng, đăng ký, lịch học*...).  
    Chatbot sẽ tự động gợi ý những từ phù hợp.

    **2. Hoặc chọn từ khóa ở thanh bên**  
    📂 Chọn một chủ đề và từ khóa trong thanh bên trái để xem câu trả lời.

    **3. Dữ liệu tự động cập nhật**  
    📂 Dữ liệu được lấy từ GitHub và làm sạch trước khi hiển thị.  
    Hệ thống chỉ giữ lại phiên bản mới nhất của mỗi từ khóa.

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

    # ✅ Keep only the latest version of each "key word"
    combined = combined.drop_duplicates(subset="key word", keep="last")

    # ✅ Remove duplicate descriptions
    dupes = combined[combined.duplicated("description", keep=False)].copy()
    removed_duplicates = dupes[dupes.duplicated("description", keep="first")]
    cleaned_data = combined.drop_duplicates(subset="description", keep="first")

    return cleaned_data, removed_duplicates

# === Step 3: Load data ===
csv_files = get_csv_file_links()
data, removed_duplicates = load_csvs(csv_files)

# === Step 4: UI Logic ===
if not data.empty:
    all_keywords = sorted(data["key word"].dropna().astype(str).unique())
    all_topics = sorted(data["topic"].dropna().unique())

    # === SIDEBAR: Topic & Keyword Picker ===
    with st.sidebar:
        with st.expander("🎯 Chọn nhanh theo chủ đề & từ khóa", expanded=True):
            selected_topic = st.selectbox("📁 Chủ đề", [""] + all_topics)

            if selected_topic:
                topic_data = data[data["topic"] == selected_topic]
                topic_keywords = sorted(topic_data["key word"].dropna().astype(str).unique())
                selected_kw = st.selectbox("🔑 Từ khóa", [""] + topic_keywords)

                if selected_kw:
                    st.session_state["selected_keyword"] = selected_kw

        with st.expander("📚 Danh mục tất cả từ khóa", expanded=False):
            st.markdown("Dưới đây là toàn bộ danh sách từ khóa theo từng chủ đề:")

            for topic in all_topics:
                st.markdown(f"#### 📁 {topic}")
                topic_data = data[data["topic"] == topic]
                keywords = sorted(topic_data["key word"].dropna().astype(str).unique())
                for kw in keywords:
                    st.markdown(f"- 🔑 `{kw}`")

    # === MAIN SEARCH BOX ===
    def search_fn(user_input):
        return [kw for kw in all_keywords if user_input.lower() in kw.lower()]

    selected_keyword = st_searchbox(
        search_fn,
        key="keyword_search",
        label="🔍 Gõ từ khóa",
        placeholder="Ví dụ: học phí, học bổng, đăng ký..."
    )

    if selected_keyword:
        st.session_state["selected_keyword"] = selected_keyword

    # === RESULT: Show chatbot response ===
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
