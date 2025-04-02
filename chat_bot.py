import pandas as pd
import streamlit as st
import requests
from streamlit_searchbox import st_searchbox

# === App Title ===
st.set_page_config(page_title="Call Center Chatbot", layout="wide")
st.title("\ud83d\udcde Call Center Chatbot")

# === Session state setup ===
if "selected_keyword" not in st.session_state:
    st.session_state["selected_keyword"] = None
if "pinned_keywords" not in st.session_state:
    st.session_state["pinned_keywords"] = []
if "multi_filter_keywords" not in st.session_state:
    st.session_state["multi_filter_keywords"] = []

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
        st.error(f"\u274c L\u1ed7i khi k\u1ebft n\u1ed1i t\u1edbi GitHub: {e}")
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
            st.warning(f"\u26a0\ufe0f L\u1ed7i \u0111\u1ecdc {name}: {e}")

    combined = combined.drop_duplicates(subset="key word", keep="last")
    combined = combined.drop_duplicates(subset="description", keep="first")

    return combined

# === Load data ===
csv_files = get_csv_file_links()
data = load_csvs(csv_files)

if not data.empty:
    all_keywords = sorted(data["key word"].dropna().astype(str).unique())
    all_topics = sorted(data["topic"].dropna().unique())

    def set_selected_keyword(keyword):
        st.session_state["selected_keyword"] = keyword

    # === Sidebar ===
    with st.sidebar:
        st.markdown("## \ud83d\udd39 T\u1ef1 ch\u1ecdn nhanh")

        # === Pin Area ===
        if st.session_state["pinned_keywords"]:
            st.markdown("### \ud83d\udccc T\u1eeb kho\u00e1 \u0111\u00e3 ghim")
            for pk in st.session_state["pinned_keywords"]:
                if st.button(f"\ud83d\udd10 {pk}", key=f"pin-{pk}"):
                    set_selected_keyword(pk)

        # === Multi-filter select ===
        st.markdown("### \ud83e\uddf0 L\u1ecdc nhi\u1ec1u t\u1eeb kho\u00e1")
        selected_multi = st.multiselect("Ch\u1ecdn nhi\u1ec1u t\u1eeb kho\u00e1:", all_keywords)
        st.session_state["multi_filter_keywords"] = selected_multi

        # === Browse by topic ===
        st.markdown("### \ud83d\udcc2 Duy\u1ec7t theo ch\u1ee7 \u0111\u1ec1")
        for topic in all_topics:
            with st.expander(f"\ud83d\udcc1 {topic}", expanded=False):
                topic_data = data[data["topic"] == topic]
                topic_keywords = sorted(topic_data["key word"].dropna().astype(str).unique())
                for kw in topic_keywords:
                    cols = st.columns([0.8, 0.2])
                    if cols[0].button(f"{kw}", key=f"kw-{topic}-{kw}"):
                        set_selected_keyword(kw)
                    pin_label = "\ud83d\udccc" if kw in st.session_state["pinned_keywords"] else "\u2606"
                    if cols[1].button(pin_label, key=f"pin-btn-{topic}-{kw}"):
                        if kw in st.session_state["pinned_keywords"]:
                            st.session_state["pinned_keywords"].remove(kw)
                        else:
                            st.session_state["pinned_keywords"].insert(0, kw)

    # === Search box ===
    def search_fn(user_input):
        return [kw for kw in all_keywords if user_input.lower() in kw.lower()]

    selected_keyword = st_searchbox(
        search_fn,
        key="keyword_search",
        label="\ud83d\udd0d G\u00f5 t\u1eeb kho\u00e1",
        placeholder="V\u00ed d\u1ee5: h\u1ecdc ph\u00ed, h\u1ecdc b\u1ed5ng..."
    )
    if selected_keyword:
        set_selected_keyword(selected_keyword)

    # === Display Results ===
    if st.session_state["multi_filter_keywords"]:
        st.subheader("\ud83d\udd0d K\u1ebf t\u1ee3 theo nhi\u1ec1u t\u1eeb kho\u00e1:")
        for kw in st.session_state["multi_filter_keywords"]:
            matches = data[data["key word"].str.lower().str.contains(kw.lower(), na=False)]
            for _, row in matches.iterrows():
                st.write(f"\ud83e\udd16 **{kw}**: {row['description']}")
    elif st.session_state["selected_keyword"]:
        kw = st.session_state["selected_keyword"]
        matches = data[data["key word"].str.lower().str.contains(kw.lower(), na=False)]
        if not matches.empty:
            for _, row in matches.iterrows():
                st.write("\ud83e\udd16 **Bot:**", row["description"])
        else:
            st.info("\u26a0\ufe0f Kh\u00f4ng t\u00ecm th\u1ea5y m\u00f4 t\u1ea3 cho t\u1eeb kho\u00e1 n\u00e0y.")
else:
    st.error("\u26a0\ufe0f Kh\u00f4ng t\u00ecm th\u1ea5y d\u1eef li\u1ec7u h\u1ee3p l\u1ec7.")
