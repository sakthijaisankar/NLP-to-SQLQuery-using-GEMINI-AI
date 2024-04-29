import streamlit as st
import pandas as pd
import sqlite3
from langchain.llms import GooglePalm
from langchain_experimental.sql import SQLDatabaseChain
from langchain.utilities import SQLDatabase
import re
from io import StringIO
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access API key from environment variables
api_key = os.environ.get("API_KEY")

page_bg_img = """
<style>
[data-testid="stAppViewContainer"]{
background-image: url("https://images.pexels.com/photos/1261728/pexels-photo-1261728.jpeg");
background-size: cover;
}

[data-testid="stHeader"]{
background-color: rgba(0, 0, 0, 0);   
}
[data-testid="stToolbar"]{
right: 2rem   
}

</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)


# Main function to run the Streamlit app
def main():
    # Page title
    st.title('LangChain SQL Query App')
    

    # Connect to existing SQLite database
    conn = sqlite3.connect('my_database.db')

    # Connect SQLite database to LangChain
    llm = GooglePalm(google_api_key=api_key, temperature=0.2)
    db = SQLDatabase.from_uri("sqlite:///my_database.db")
    db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True)

    # Function to execute SQL query using LangChain
    def execute_query(query):
        stdout_saved = sys.stdout
        sys.stdout = StringIO()
        db_chain(query)
        output = sys.stdout.getvalue()
        sys.stdout = stdout_saved
        pattern = r"SQLQuery:(.*)"
        match = re.search(pattern, output)
        sql_query = match.group(1).strip() if match else None
        clean_sql_query = re.sub(r'\x1b\[\d{1,2}(;\d{1,2}){0,2}m', '', sql_query)
        return clean_sql_query.strip()

    # User input for SQL query
    query = st.text_input('Enter your SQL-like query:', ' ')

    # Execute query button
    if st.button('Execute Query'):
        try:
            sql_query = execute_query(query)
            result = pd.read_sql_query(sql_query, conn)
            st.write(sql_query)
            st.dataframe(result)
        except Exception as e:
            st.error(f'An error occurred: {e}')

if __name__ == '__main__':
    main()


