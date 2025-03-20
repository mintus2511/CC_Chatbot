import pandas as pd
import streamlit as st 
import numpy as np 
import os 
#streamlit 
st.title("CC - CHATBOT")
#st.sidebar.header("Chat history")
#save the csv file for cloud
cloud_path = "data.csv"

# Setup
cc = pd.read_csv(r"cc - Trang tính1.csv") 
program = pd.read_csv(r"program  - Trang tính1.csv") 
other = pd.read_csv(r"other  - Trang tính1.csv")
ts = pd.read_csv(r"ts  - Trang tính1.csv")
hard = pd.read_csv(r"hard - Trang tính1.csv")
hb = pd.read_csv(r"hb - Trang tính1.csv")
major = pd.read_csv(r"major  - Trang tính1.csv")


# #save the history file 
# history_file = "data"
# def load_chat_data():
#     all_dataframes = {}
#     for file in os.listdir(history_file):
#         if file.endswith(".csv"):
#             df = pd.read_csv(os.path.join(history_file, file))
#             all_dataframes[file] = df
#     return all_dataframes
# def save_uploaded_file(uploaded_file):
#     file_path = os.path.join(history_file, uploaded_file.name)
#     with open(file_path, "wb") as f:
#         f.write(uploaded_file.getbuffer())
#     return file_path
# chatbot_data = load_chat_data()



# Topics and keyword datasets
exist_program = {
    "cc": cc,
    "program": program,
    "other": other,
    "ts": ts,
    "hard": hard,
    "hb": hb,
    "major": major,
}

#add pdf or csv
csv_file = st.file_uploader("Upload csv follow format:(column 1: key word, column 2: description):", type=["csv"])
if csv_file is not None:
    try:
        # file_path = save_uploaded_file(csv_file)
        new_data = pd.read_csv(csv_file)
        #save this to cloud 
        df = new_data.to_csv(cloud_path, index=False)
        st.success("CSV filed add for team success")
        st.session_state["uploaded"] = new_data
        exist_program["Uploaded"] = new_data
        st.write("CSV file has been added. Keywords and Descriptions:")
        st.dataframe(new_data)
        # for k, d in zip(key, descriptions):
        #     st.write(f"**{k}:** {d}")
            # chatbot_data = load_chat_data()
    except Exception as e:
            st.write("Please check your data format. If issues persist, contact Quynh for assistance.")


# Chatbot response class
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
#streamlit 
topic_options = st.selectbox("Choose a topic",list(exist_program.keys()))
if topic_options:
    data = Data(exist_program[topic_options])
    select = st.selectbox("Choose a keyword", data.list_keywords())
    if select:
        bot_response = data.description(select)
        st.write("Bot:", bot_response)
