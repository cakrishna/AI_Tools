import streamlit as st
import sqlite3
# import google.generativeai as genai

from langchain_groq import ChatGroq

llm = ChatGroq(
    temperature=0, 
    groq_api_key='API_Key_Here', 
    model_name="llama-3.3-70b-versatile" 
    # model_name="gemma2-9b-it"
)

## Configure Genai Key
# genai.configure(api_key='YOUR_API_KEY')

## Define Your Prompt
prompt=[
    """
    You are an expert in converting English questions to SQL query!
    The SQL database has the name MOVIE and has the following columns 
    - Name, Revenue, Year, Universe
       
    For example,
    Example 1 - How many entries of records are present?, 
    the SQL command will be something like this SELECT COUNT(*) FROM MOVIE ;
    
    Example 2 - Tell me all the movies in Marvel Universe?, 
    the SQL command will be something like this SELECT * FROM MOVIE 
    where Universe="Marvel"; 

    oytput without braces
    
    also the sql code should not have ``` 
    in beginning or end and sql word in output    

    """
]

## Function to retrieve query from the database
def read_sql_query(sql,db):
    conn=sqlite3.connect(db)
    cur=conn.cursor()
    cur.execute(sql)
    rows=cur.fetchall()
    conn.commit()
    conn.close()
    for row in rows:
        print(row)
    return rows
    
## Function To Load Google Gemini Model and provide queries as response
def get_gemini_response(question,prompt):
    # model=genai.GenerativeModel('gemini-pro')
    model=llm
    response=model.invoke([prompt[0],question])
    return response.content


## Streamlit App
st.set_page_config(page_title="English questions to SQL query")
st.header("Retrieve Data from CSV")

question=st.text_input("Input: ",key="input")

# The content of the Submit button
submit=st.button("Get Answers")

# if submit is clicked
if submit:
    response=get_gemini_response(question,prompt)
    print(response)
    response=read_sql_query(response,"movie.db")
    st.subheader("The Response is")
    for row in response:
        print(row)
        st.header(row)