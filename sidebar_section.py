import streamlit as st
from streamlit_searchbox import st_searchbox

def render_sidebar(
    user_id,
    all_topics,
    filtered_keywords,
    pinned_df,
    search_fn,
    set_selected_keyword,
    save_pinned_keywords
):
    # === User info + Dark mode (hiển thị ở theme.py) ===
    st.markdown(f"👤 **Xin chào:** `{user_id}`")
    st.markdown("---")
    st.markdown("### 🌓 Giao diện")
    # Nút chuyển theme nằm trong theme.py

    # === Bộ lọc chủ đề và từ khóa ===
    st.markdown("### 🧭 Bộ lọc nội dung")
    with st.expander("📂 Chọn chủ đề", expanded=True):
        selected_topics = st.multiselect("Chọn chủ đề:", all_topics)

    with st.expander("🧠 Chọn nhiều từ khóa", expanded=False):
        selected_multi = st.multiselect("Chọn nhiều từ khóa:", sorted(filtered_keywords))

    st.session_state["selected_topics"] = selected_topics
    st.session_state["multi_filter_keywords"] = selected_multi

    # === Từ khóa đã ghim ===
    if st.session_state.get("pinned_keywords", []):
        st.markdown("---")
        with st.expander("📌 Từ khóa đã ghim", expanded=False):
            if st.button("❌ Xóa tất cả"):
                st.session_state["pinned_keywords"] = []
                save_pinned_keywords([])
                st.rerun()

            for topic in sorted(pinned_df["topic"].unique()):
                with st.expander(f"📂 {topic}", expanded=False):
                    for kw in sorted(pinned_df[pinned_df["topic"] == topic]["key word"].unique()):
                        if st.button(f"📍 {kw}", key=f"pinned-{kw}"):
                            set_selected_keyword(kw)
                            st.rerun()

    # === Searchbox nhanh ===
    st.markdown("---")
    st.markdown("### 🔍 Tìm kiếm nhanh")
    selected_keyword = st_searchbox(
        search_fn,
        key="keyword_search",
        label="Gõ từ khóa...",
        placeholder="Ví dụ: học phí, học bổng..."
    )
    if selected_keyword:
        set_selected_keyword(selected_keyword)
        st.rerun()
