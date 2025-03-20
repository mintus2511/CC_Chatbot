import pandas as pd
import streamlit as st 
import requests

# Streamlit UI
st.title("Call Center CHATBOT")

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
        
        if not csv_files:
            st.warning("No CSV files found in the repository.")
        
        return csv_files
    except requests.exceptions.RequestException as e:
        st.error("Cannot fetch data. Contact Quỳnh, Tú, or Thạch for debugging.")
        return {}

def load_data(url):
    try:
        df = pd.read_csv(url, encoding="utf-8")
        df.columns = df.columns.str.lower().str.strip()  # Normalize column names
        required_columns = {"key word", "description"}
        
        if not required_columns.issubset(df.columns):
            st.error(f"CSV missing required columns: {required_columns - set(df.columns)}")
            return None
        
        return df
    except Exception as e:
        st.error(f"Error loading data from {url}. Please contact Quỳnh.")
        return None

# Load CSV files from GitHub
csv_files = get_csv_file()
exist_program = {name: load_data(url) for name, url in csv_files.items() if load_data(url) is not None}

# Debugging Output
if not exist_program:
    st.error("No valid CSV data found. Please check the repository.")

# Chatbot Response Class
class Data:
    def __init__(self, dataframe):
        self.dataframe = dataframe
        self.activate = dataframe['key word'].astype(str).tolist() if 'key word' in dataframe.columns else []

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
