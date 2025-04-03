import pandas as pd
import streamlit as st
import requests
import json
import uuid
import os
from streamlit_searchbox import st_searchbox
from datetime import datetime, timedelta

# === App Title ===
st.set_page_config(page_title="Call Center Chatbot", layout="wide")
st.title("📞 Call Center Chatbot")

# === Constants ===
PINNED_FILE = "pinned_keywords.json"
UPLOADED_FILE = "uploaded_keywords.csv"

# === User Identification via Cookie ===
if "user_id" not in st.session_state:
    user_id = st.query_params.get("uid", None)
    if not user_id:
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        st.query_params["uid"] = user_id
    st.session_state["user_id"] = user_id

user_id = st.session_state["user_id"]

# === Theme ===
from theme import apply_theme
apply_theme(user_id=user_id)

# === Load pinned keywords ===
def load_pinned_keywords():
    try:
        with open(PINNED_FILE, "r") as f:
            all_pins = json.load(f)
            return all_pins.get(user_id, [])
    except:
        return []

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

# === Session state ===
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
if "is_authorized" not in st.session_state:
    st.session_state["is_authorized"] = False

# === Load Data ===
all_dataframes = []
if os.path.exists(UPLOADED_FILE):
    try:
        uploaded_df = pd.read_csv(UPLOADED_FILE)
        uploaded_df.columns = uploaded_df.columns.str.lower().str.strip()
        if {"key word", "description", "topic"}.issubset(uploaded_df.columns):
            all_dataframes.append(uploaded_df)
            st.session_state["uploaded_data"] = uploaded_df
    except Exception as e:
        st.warning(f"⚠️ Không thể đọc file đã lưu: {e}")

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
        st.warning(f"⚠️ Lỗi khi lấy danh sách file từ GitHub: {e}")
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
                combined = pd.concat([combined, df], ignore_index=True)
        except Exception as e:
            st.warning(f"⚠️ Không thể đọc {name} từ GitHub: {e}")
    return combined.drop_duplicates(subset="key word", keep="last").drop_duplicates(subset="description", keep="first")

csv_files = get_csv_file_links()
github_df = load_csvs(csv_files)
if not github_df.empty:
    all_dataframes.append(github_df)

if all_dataframes:
    data = pd.concat(all_dataframes, ignore_index=True)
else:
    data = pd.DataFrame(columns=["key word", "description", "topic"])

if "uploaded_data" in st.session_state:
    data = pd.concat([data, st.session_state["uploaded_data"]], ignore_index=True)
    data = data.drop_duplicates(subset="key word", keep="last").drop_duplicates(subset="description", keep="first")

# === Sidebar layout ===
with st.sidebar:
    st.markdown(f"👤 **Xin chào:** `{user_id}`")
    st.markdown("---")
    st.markdown("### 🌓 Giao diện")
    # (Nút chuyển theme nằm trong apply_theme)

    st.markdown("### 🧭 Bộ lọc nội dung")
    with st.expander("📂 Chọn chủ đề", expanded=True):
        all_topics = sorted(data["topic"].dropna().unique())
        selected_topics = st.multiselect("Chọn chủ đề:", all_topics)
    with st.expander("🧠 Chọn nhiều từ khóa", expanded=False):
        all_keywords = sorted(data["key word"].dropna().astype(str).unique())
        filtered_keywords = data[data["topic"].isin(selected_topics)]["key word"].unique() if selected_topics else all_keywords
        selected_multi = st.multiselect("Chọn nhiều từ khóa:", sorted(filtered_keywords))

    st.session_state["selected_topics"] = selected_topics
    st.session_state["multi_filter_keywords"] = selected_multi

    if st.session_state["pinned_keywords"]:
        st.markdown("---")
        with st.expander("📌 Từ khóa đã ghim", expanded=False):
            if st.button("❌ Xóa tất cả"):
                st.session_state["pinned_keywords"] = []
                save_pinned_keywords([])
                st.rerun()
            pinned_df = data[data["key word"].isin(st.session_state["pinned_keywords"])]
            for topic in sorted(pinned_df["topic"].unique()):
                with st.expander(f"📂 {topic}", expanded=False):
                    for kw in sorted(pinned_df[pinned_df["topic"] == topic]["key word"].unique()):
                        if st.button(f"📍 {kw}", key=f"pinned-{kw}"):
                            st.session_state["selected_keyword"] = kw
                            st.session_state["trigger_display"] = True
                            st.rerun()

    st.markdown("---")
    st.markdown("### 🔍 Tìm kiếm nhanh")
    def search_fn(user_input):
        return [kw for kw in all_keywords if user_input.lower() in kw.lower()]
    selected_keyword = st_searchbox(
        search_fn,
        key="keyword_search",
        label="Gõ từ khóa...",
        placeholder="Ví dụ: học phí, học bổng..."
    )
    if selected_keyword:
        st.session_state["selected_keyword"] = selected_keyword
        st.session_state["trigger_display"] = True
        st.rerun()

# === Hiển thị nội dung ===
def display_bot_response(keyword, description, topic):
    st.chat_message("user").markdown(f"🔍 **Từ khóa:** `{keyword}`")
    st.chat_message("assistant").markdown(f"**📂 Chủ đề:** `{topic}`\n\n{description}")
    st.session_state["chat_history"].append({
        "keyword": keyword,
        "description": description,
        "topic": topic
    })

if st.session_state["multi_filter_keywords"]:
    st.subheader("📋 Kết quả theo nhiều từ khóa:")
    for kw in st.session_state["multi_filter_keywords"]:
        matches = data[data["key word"].str.lower() == kw.lower()]
        for _, row in matches.iterrows():
            display_bot_response(kw, row["description"], row["topic"])
elif st.session_state["selected_keyword"] and st.session_state["trigger_display"]:
    st.session_state["trigger_display"] = False
    kw = st.session_state["selected_keyword"]
    matches = data[data["key word"].str.lower() == kw.lower()]
    if not matches.empty:
        for _, row in matches.iterrows():
            display_bot_response(kw, row["description"], row["topic"])
    else:
        st.info("⚠️ Không tìm thấy mô tả cho từ khóa này.")

# === Lịch sử hội thoại ===
if st.session_state["chat_history"]:
    st.markdown("---")
    with st.expander("💬 Xem lại lịch sử cuộc trò chuyện", expanded=False):
        if st.button("🗑️ Xóa lịch sử cuộc trò chuyện"):
            st.session_state["chat_history"] = []
            st.rerun()
        for msg in st.session_state["chat_history"]:
            st.chat_message("user").markdown(f"🔍 **Từ khóa:** `{msg['keyword']}`")
            st.chat_message("assistant").markdown(f"**📂 Chủ đề:** `{msg['topic']}`\n\n{msg['description']}")
