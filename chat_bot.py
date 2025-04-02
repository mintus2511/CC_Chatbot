import pandas as pd
import streamlit as st
import requests
import json
import uuid
from streamlit_searchbox import st_searchbox
from datetime import datetime, timedelta

# === App Title ===
st.set_page_config(page_title="Call Center Chatbot", layout="wide")
st.title("📞 Call Center Chatbot")

# === Constants ===
PINNED_FILE = "pinned_keywords.json"

# === User Identification via Cookie ===
if "user_id" not in st.session_state:
    user_id = st.query_params.get("uid", None)
    if not user_id:
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        st.query_params["uid"] = user_id
    st.session_state["user_id"] = user_id

user_id = st.session_state["user_id"]

# === Đăng xuất / Tạo người dùng mới ===
with st.sidebar:
    if st.button("🔄 Đăng xuất / Tạo người dùng mới"):
        new_id = f"user_{uuid.uuid4().hex[:8]}"
        st.query_params["uid"] = new_id
        st.rerun()

    

# === Load pinned keywords from file ===
def load_pinned_keywords():
    try:
        with open(PINNED_FILE, "r") as f:
            all_pins = json.load(f)
            return all_pins.get(user_id, [])
    except:
        return []

# === Save pinned keywords to file ===
def save_pinned_keywords(pins):
    all_pins = {}
    try:
        with open(PINNED_FILE, "r") as f:
            all_pins = json.load(f)
    except:
        pass
    all_pins[user_id] = pins
    with open(PINNED_FILE, "w") as f:
        json.dump(all_pins, f)

# === Session state setup ===
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "selected_keyword" not in st.session_state:
    st.session_state["selected_keyword"] = None
if "pinned_keywords" not in st.session_state:
    st.session_state["pinned_keywords"] = load_pinned_keywords()
if "multi_filter_keywords" not in st.session_state:
    st.session_state["multi_filter_keywords"] = []
if "selected_topics" not in st.session_state:
    st.session_state["selected_topics"] = []
if "trigger_display" not in st.session_state:
    st.session_state["trigger_display"] = False

def display_bot_response(keyword, description, topic):
    st.chat_message("user").markdown(f"🔍 **Từ khóa:** `{keyword}`")
    st.chat_message("assistant").markdown(
        f"**📂 Chủ đề:** `{topic}`\n\n{description}"
    )
    st.session_state["chat_history"].append({
        "keyword": keyword,
        "description": description,
        "topic": topic
    })

# === Co-lead Authorization ===
if "is_authorized" not in st.session_state:
    st.session_state["is_authorized"] = False

if not st.session_state["is_authorized"]:
    code = st.text_input("🔑 Nhập mã truy cập Co-lead")
    if code == "COLEAD2024":
        st.session_state["is_authorized"] = True
        st.success("✅ Xác thực thành công. Bạn có quyền tải lên dữ liệu mới.")
    elif code:
        st.error("❌ Mã truy cập không đúng")

# === Upload CSV to update keywords ===
if st.session_state["is_authorized"]:
    st.markdown("---")
    st.subheader("📤 Tải lên file CSV cập nhật từ khóa")
    uploaded_file = st.file_uploader("Chọn file CSV để cập nhật từ khóa và mô tả", type="csv")
    if uploaded_file is not None:
        try:
            update_df = pd.read_csv(uploaded_file)
            update_df.columns = update_df.columns.str.lower().str.strip()
            if {"key word", "description"}.issubset(update_df.columns):
                update_df["topic"] = "Tải lên"
                st.session_state["uploaded_data"] = update_df[["key word", "description", "topic"]]
                st.success("✅ File đã được tải lên thành công. Dữ liệu sẽ hiển thị cùng các chủ đề khác.")
            else:
                st.error("❌ File không đúng định dạng. Cần có cột 'key word' và 'description'.")
                data = data.drop_duplicates(subset="key word", keep="last")
                data = data.drop_duplicates(subset="description", keep="first")
                st.success("✅ Đã cập nhật dữ liệu từ file tải lên.")
                else:
                    st.error("❌ File không đúng định dạng. Cần có cột 'key word' và 'description'.")
        except Exception as e:
            st.error(f"❌ Lỗi khi đọc file: {e}")

# === User Guide ===

# === Co-lead Authorization dưới cùng sidebar ===
with st.sidebar:
    with st.expander("👤 Khu vực dành cho Co-lead (ẩn mặc định)", expanded=False):
        if "is_authorized" not in st.session_state:
            st.session_state["is_authorized"] = False

        if not st.session_state["is_authorized"]:
            code = st.text_input("🔑 Nhập mã truy cập Co-lead", type="password")
            if code == "COLEAD2024":
                st.session_state["is_authorized"] = True
                st.success("✅ Xác thực thành công. Bạn có quyền tải lên dữ liệu mới.")
            elif code:
                st.error("❌ Mã truy cập không đúng")

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

csv_files = get_csv_file_links()
data = load_csvs(csv_files)

# Nếu có dữ liệu upload từ co-lead, thêm vào
if "uploaded_data" in st.session_state:
    data = pd.concat([data, st.session_state["uploaded_data"]], ignore_index=True)
    data = data.drop_duplicates(subset="key word", keep="last")
    data = data.drop_duplicates(subset="description", keep="first")

def set_selected_keyword(keyword):
    st.session_state["selected_keyword"] = keyword
    st.session_state["trigger_display"] = True

if not data.empty:
    all_keywords = sorted(data["key word"].dropna().astype(str).unique())
    all_topics = sorted(data["topic"].dropna().unique())

    with st.sidebar:
        st.markdown("### 🧭 Lọc theo chủ đề")
        selected_topics = st.multiselect("Chọn chủ đề:", all_topics)
        st.session_state["selected_topics"] = selected_topics

        if st.session_state["pinned_keywords"]:
            st.markdown("### 📌 Từ khóa đã ghim")
            if st.button("🧼 Xóa toàn bộ từ khóa đã ghim"):
                st.session_state["pinned_keywords"] = []
                save_pinned_keywords([])
                st.rerun()
            if st.button("🗑️ Xóa tất cả từ khóa đã ghim"):
                st.session_state["pinned_keywords"] = []
                save_pinned_keywords([])
                st.rerun()
            pinned_df = data[data["key word"].isin(st.session_state["pinned_keywords"])]
            for topic in sorted(pinned_df["topic"].unique()):
                with st.expander(f"📁 {topic}", expanded=False):
                    for kw in sorted(pinned_df[pinned_df["topic"] == topic]["key word"].unique()):
                        if st.button(f"📍 {kw}", key=f"pinned-{kw}"):
                            set_selected_keyword(kw)
                            st.rerun()

        st.markdown("### 🧠 Lọc nhiều từ khóa")
        filtered_keywords = data[data["topic"].isin(selected_topics)]["key word"].unique() if selected_topics else all_keywords
        selected_multi = st.multiselect("Chọn nhiều từ khóa:", sorted(filtered_keywords))
        st.session_state["multi_filter_keywords"] = selected_multi

        st.markdown("### 📚 Danh mục từ khóa")
        topics_to_show = selected_topics if selected_topics else all_topics
        for topic in topics_to_show:
            with st.expander(f"📁 {topic}", expanded=False):
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
                        save_pinned_keywords(st.session_state["pinned_keywords"])

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

    if st.session_state["multi_filter_keywords"]:
        st.subheader("📋 Kết quả theo nhiều từ khóa:")
        for kw in st.session_state["multi_filter_keywords"]:
            matches = data[data["key word"].str.lower().str.contains(kw.lower(), na=False)]
            for _, row in matches.iterrows():
                display_bot_response(kw, row["description"], row["topic"])
    elif st.session_state["selected_keyword"] and st.session_state["trigger_display"]:
        st.session_state["trigger_display"] = False
        kw = st.session_state["selected_keyword"]
        matches = data[data["key word"].str.lower().str.contains(kw.lower(), na=False)]
        if not matches.empty:
            for _, row in matches.iterrows():
                display_bot_response(kw, row["description"], row["topic"])
        else:
            st.info("⚠️ Không tìm thấy mô tả cho từ khóa này.")
else:
    st.error("⚠️ Không tìm thấy dữ liệu hợp lệ.")

# === Hiển thị lịch sử hội thoại (ẩn mặc định và có nút xóa) ===
if st.session_state["chat_history"]:
    st.markdown("---")
    with st.expander("💬 Xem lại lịch sử cuộc trò chuyện", expanded=False):
        if st.button("🗑️ Xóa lịch sử cuộc trò chuyện"):
            st.session_state["chat_history"] = []
            st.rerun()
        for msg in st.session_state["chat_history"]:
            st.chat_message("user").markdown(f"🔍 **Từ khóa:** `{msg['keyword']}`")
            st.chat_message("assistant").markdown(f"**📂 Chủ đề:** `{msg['topic']}`\\n\\n{msg['description']}")
