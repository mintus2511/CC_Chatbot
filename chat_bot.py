import pandas as pd
import streamlit as st 
import requests

# Streamlit UI
st.title("CC - CHATBOT")

# GitHub API Setup
GITHUB_USER = "Menbeo"
GITHUB_REPO = "-HUHU-"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/"

def get_csv_file():
    try:
        response = requests.get(GITHUB_API_URL)
        response.raise_for_status()
        files = response.json()
        csv_files = {file["name"]: file["download_url"]
                     for file in files if file["name"].endswith(".csv")}
        return csv_files
    except requests.exceptions.RequestException:
        st.error("Cannot fetch data. Contact Quynh, Tú, or Thạch for debugging.")
        return {}

def load_data(url):
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.lower().str.strip()  # Normalize column names
        return df
    except Exception:
        st.error("Error loading data. Please contact Quynh.")
        return None

# Load CSV files from GitHub
csv_files = get_csv_file()
exist_program = {name: load_data(url) for name, url in csv_files.items() if load_data(url) is not None}

# Class to handle chatbot responses
class Data:
    def __init__(self, dataframe):
        self.dataframe = dataframe
        if 'key word' in dataframe.columns and 'description' in dataframe.columns:
            self.activate = dataframe['key word'].astype(str).tolist()
        else:
            self.activate = []  # Handle missing columns
    
    def list_keywords(self):
        return self.activate
    
    def description(self, keyword):
        if keyword in self.activate:
            responses = self.dataframe.loc[self.dataframe['key word'] == keyword, 'description']
            return responses.iloc[0] if not responses.empty else "No description available."
        return "No data available. If you want to add, please type 'add'."

# Streamlit UI Components
if exist_program:
    topic_options = st.selectbox("Choose a topic", list(exist_program.keys()))
    if topic_options:
        data = Data(exist_program[topic_options])
        if data.list_keywords():
            select = st.selectbox("Choose a keyword", data.list_keywords())
            if select:
                bot_response = data.description(select)
                st.write("Bot:", bot_response)
        else:
            st.warning("No keywords available for this topic.")
else:
    st.error("No CSV files found. Please check the GitHub repository.")
