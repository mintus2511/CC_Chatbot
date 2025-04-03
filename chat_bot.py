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
if "is_authorized" not in st.session_state:
    st.session_state["is_authorized"] = False 

# === Load uploaded file nếu đã tồn tại ===
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

# === Load GitHub CSVs nếu có ===
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
    return combined

csv_files = get_csv_file_links()
github_df = load_csvs(csv_files)
if not github_df.empty:
    all_dataframes.append(github_df)

# Gộp toàn bộ dữ liệu từ GitHub + file upload để có thể chỉnh sửa
if all_dataframes:
    all_data_combined = pd.concat(all_dataframes, ignore_index=True)
else:
    all_data_combined = pd.DataFrame(columns=["key word", "description", "topic"])

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

# === Co-lead Authorization Section ===
with st.sidebar:
    st.markdown("---")
    with st.expander("Admin Request", expanded=False):
        if not st.session_state["is_authorized"]:
            code = st.text_input("🔑 Vui lòng nhập password", type="password", key="colead_password")
            if code == "ADMIN123@":
                st.session_state["is_authorized"] = True
                st.success("✅ Xác thực thành công. Bạn có quyền tải lên dữ liệu mới.")
                st.rerun()
            elif code:
                st.error("❌ Mã truy cập không đúng")
        else:
            st.success("🔓 Bạn đang ở chế độ Admin")
            if st.button("🚪 Thoát chế độ Admin"):
                st.session_state["is_authorized"] = False
                st.success("✅ Bạn đã thoát khỏi chế độ Admin.")
                st.rerun()

# === Upload hoặc Quản lý topic ===
if st.session_state["is_authorized"]:
    st.markdown("---")
    st.subheader("🛠️ Hành động dành cho Admin")
    co_action = st.radio(
    "Chọn hành động:",
    ["📤 Tải file CSV mới", "➕ Thêm từ khóa", "📝 Chỉnh sửa topic/key word/description", "🗑️ Xoá topic/key word"],
        horizontal=True,
        key="co_action"
    )

    if co_action == "📤 Tải file CSV mới":
        upload_mode = st.radio(
            "Chọn chế độ tải lên:",
            ["🔄 Cập nhật từ khóa đã có", "🆕 Tạo topic mới từ file"],
            horizontal=True,
            key="upload_mode"
        )

        uploaded_files = st.file_uploader("Chọn file CSV", type="csv", accept_multiple_files=True)

        if uploaded_files:
            for uploaded_file in uploaded_files:
                try:
                    update_df = pd.read_csv(uploaded_file)
                    update_df.columns = update_df.columns.str.lower().str.strip()
                    if {"key word", "description"}.issubset(update_df.columns):
                        if "uploaded_data" in st.session_state:
                            old_df = st.session_state["uploaded_data"]
                        elif os.path.exists(UPLOADED_FILE):
                            old_df = pd.read_csv(UPLOADED_FILE)
                            old_df.columns = old_df.columns.str.lower().str.strip()
                        else:
                            old_df = pd.DataFrame(columns=["key word", "description", "topic"])

                        if "topic" not in update_df.columns:
                            update_df["topic"] = None

                        if st.session_state["upload_mode"] == "🔄 Cập nhật từ khóa đã có":
                            merged_df = pd.merge(update_df, old_df[['key word', 'topic']], on='key word', how='left', suffixes=('', '_old'))
                            merged_df['topic'] = merged_df['topic'].combine_first(merged_df['topic_old'])
                            merged_df.drop(columns=['topic_old'], inplace=True)
                            merged_df['topic'] = merged_df['topic'].fillna('Tải lên')
                        else:
                            default_topic = os.path.splitext(uploaded_file.name)[0]
                            custom_topic = st.text_input(f"📝 Đặt tên cho topic mới cho file `{uploaded_file.name}`:", value=default_topic, key=f"topic_name_{uploaded_file.name}")
                            update_df['topic'] = custom_topic
                            merged_df = update_df

                        # Gộp vào dữ liệu đang có trong session
                        if "uploaded_data" in st.session_state:
                            st.session_state["uploaded_data"] = pd.concat([
                                st.session_state["uploaded_data"],
                                merged_df[["key word", "description", "topic"]]
                            ], ignore_index=True)
                        else:
                            st.session_state["uploaded_data"] = merged_df[["key word", "description", "topic"]]

                        # Lưu vào file
                        st.session_state["uploaded_data"].to_csv(UPLOADED_FILE, index=False)
                        st.success(f"✅ Đã xử lý và lưu file: `{uploaded_file.name}`")
                    else:
                        st.error(f"❌ File `{uploaded_file.name}` không đúng định dạng. Cần có cột 'key word' và 'description'.")
                except Exception as e:
                    st.error(f"❌ Lỗi khi đọc file `{uploaded_file.name}`: {e}")
    elif co_action == "➕ Thêm từ khóa":
        st.markdown("---")
        st.subheader("🧾 Nhập từ khóa mới")

    # ✅ Hiển thị chọn hoặc nhập chủ đề mới - nằm ngoài form để phản ứng ngay lập tức
        existing_topics = sorted(all_data_combined["topic"].dropna().unique())
        topic_choice = st.selectbox(
            "📂 Chọn chủ đề (hoặc nhập mới)",
            options=["🔄 Nhập mới..."] + existing_topics,
            index=1 if existing_topics else 0,
            key="manual_topic_select"
        )

        if topic_choice == "🔄 Nhập mới...":
            topic = st.text_input("📌 Nhập tên chủ đề mới", key="manual_new_topic").strip()
        else:
            topic = topic_choice

        # ✅ Form nhập từ khóa và mô tả
        with st.form("manual_add_keyword"):
            keyword = st.text_input("🔑 Từ khóa").strip()
            description = st.text_area("📝 Mô tả").strip()

            submitted = st.form_submit_button("✅ Lưu từ khóa mới")
            if submitted:
                if keyword and description and topic:
                    new_row = pd.DataFrame([{
                        "key word": keyword,
                        "description": description,
                        "topic": topic
                    }])

                    if os.path.exists(UPLOADED_FILE):
                        df_existing = pd.read_csv(UPLOADED_FILE)
                    else:
                        df_existing = pd.DataFrame(columns=["key word", "description", "topic"])

                    df_combined = pd.concat([df_existing, new_row], ignore_index=True)
                    df_combined.to_csv(UPLOADED_FILE, index=False)

                    st.success("✅ Đã thêm từ khóa mới thành công.")
                    st.rerun()
                else:
                    st.error("❗ Vui lòng điền đầy đủ cả 3 cột.")


    elif co_action in ["📝 Chỉnh sửa topic/key word/description", "🗑️ Xoá topic/key word"]:
        st.markdown("---")
        st.subheader("🗂️ Quản lý topic và từ khóa")
        if os.path.exists(UPLOADED_FILE):
            try:
                df_all = all_data_combined.copy()
                all_topics = sorted(df_all['topic'].dropna().unique())
                topic_to_edit = st.selectbox("📂 Chọn topic:", all_topics)
                df_topic = df_all[df_all['topic'] == topic_to_edit].copy()

            # === Hiển thị bảng có thể chỉnh sửa kèm cột chọn xoá
                df_topic["🔘 Chọn xoá"] = False
                edited_df = st.data_editor(
                    df_topic,
                    num_rows="dynamic",
                    use_container_width=True,
                    key="edit_table_with_delete"
                )

            # === Lưu chỉnh sửa toàn bộ bảng
                if st.button("💾 Lưu chỉnh sửa"):
                    df_all = df_all[df_all['topic'] != topic_to_edit]
                    df_all = pd.concat([df_all, edited_df.drop(columns=["🔘 Chọn xoá"])], ignore_index=True)
                    df_all.to_csv(UPLOADED_FILE, index=False)
                    st.success("✅ Đã lưu chỉnh sửa thành công.")
                    st.rerun()

                # === Xoá từ khóa đã chọn
                if st.button("🗑️ Xoá từ khóa đã chọn"):
                    to_delete = edited_df[edited_df["🔘 Chọn xoá"] == True]
                    if not to_delete.empty:
                        df_all = df_all[~(
                            (df_all["topic"] == topic_to_edit) &
                            (df_all["key word"].isin(to_delete["key word"]))
                        )]
                        df_all.to_csv(UPLOADED_FILE, index=False)
                        st.success(f"🗑️ Đã xoá {len(to_delete)} từ khóa khỏi topic.")
                        st.rerun()
                    else:
                        st.warning("⚠️ Bạn chưa chọn từ khóa nào để xoá.")

                # === Đổi tên topic
                if co_action == "📝 Chỉnh sửa topic đã upload":
                    new_name = st.text_input("✏️ Đổi tên topic:", value=topic_to_edit)
                    if st.button("💾 Lưu tên topic mới") and new_name != topic_to_edit:
                        df_all.loc[df_all['topic'] == topic_to_edit, 'topic'] = new_name
                        df_all.to_csv(UPLOADED_FILE, index=False)
                        st.success("✅ Đã đổi tên topic thành công.")
                        st.rerun()

                # === Xoá toàn bộ topic
                elif co_action == "🗑️ Xoá topic":
                    if st.button("🗑️ Xoá toàn bộ topic này"):
                        df_all = df_all[df_all['topic'] != topic_to_edit]
                        df_all.to_csv(UPLOADED_FILE, index=False)
                        st.success(f"🗑️ Đã xoá topic '{topic_to_edit}' cùng toàn bộ từ khóa liên quan.")
                        st.rerun()
            except Exception as e:
                st.error(f"❌ Không thể quản lý topic: {e}")


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
        st.markdown("### 🧭 Chọn chủ đề (có thể chọn nhiều option)")
        selected_topics = st.multiselect("Chọn chủ đề:", all_topics)
        st.session_state["selected_topics"] = selected_topics

        if st.session_state["pinned_keywords"]:
            st.markdown("### 📌 Từ khóa đã ghim")
            if st.button("Xóa tất cả từ khóa đã ghim"):
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

        st.markdown("### 🧠 Chọn nhiều từ khóa")
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
