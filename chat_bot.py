import pandas as pd
import streamlit as st
import os 

# Streamlit
st.title("CC - CHATBOT")
st.sidebar.header("Chat history")

# Load predefined CSV files
def load_csv(filename):
    return pd.read_csv(filename) if os.path.exists(filename) else pd.DataFrame(columns=["key word", "description"])

cc = load_csv("cc - Trang tính1.csv")
program = load_csv("program - Trang tính1.csv")
other = load_csv("other - Trang tính1.csv")
ts = load_csv("ts - Trang tính1.csv")
hard = load_csv("hard - Trang tính1.csv")
hb = load_csv("hb - Trang tính1.csv")
major = load_csv("major - Trang tính1.csv")

# Lưu trữ các dataset có sẵn
exist_program = {
    "cc": cc,
    "program": program,
    "other": other,
    "ts": ts,
    "hard": hard,
    "hb": hb,
    "major": major,
}

# Upload CSV file
uploaded_file = st.file_uploader("Upload CSV (column 1: key word, column 2: description):", type=["csv"])
if uploaded_file is not None:
    try:
        new_data = pd.read_csv(uploaded_file)
        st.session_state["uploaded_data"] = new_data  # Lưu vào session để sử dụng sau
        st.write("CSV file has been added:")
        st.dataframe(new_data)
    except Exception as e:
        st.write("Error: Please check your CSV format.")

# Lưu dữ liệu CSV đã tải lên vào lịch sử chat
if "uploaded_data" in st.session_state:
    exist_program["uploaded"] = st.session_state["uploaded_data"]

# Class để xử lý chatbot data
class Data:
    def __init__(self, dataframe):
        self.dataframe = dataframe
        self.activate = dataframe['key word'].astype(str).tolist()  # Convert to list

    def list_keywords(self):
        return self.activate

    def description(self, keyword):
        if keyword in self.activate:
            responses = self.dataframe.loc[self.dataframe['key word'] == keyword, 'description']
            return responses.iloc[0]
        else:
            return "No data available. If you want to add, please type 'add'."

# Hiển thị chọn topic & keyword
topic_options = st.selectbox("Choose a topic", list(exist_program.keys()))
if topic_options:
    data = Data(exist_program[topic_options])
    select = st.selectbox("Choose a keyword", data.list_keywords())
    if select:
        bot_response = data.description(select)
        st.write("Bot:", bot_response)
