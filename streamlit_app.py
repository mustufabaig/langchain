import streamlit as st
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain.llms.openai import OpenAI
from langchain.agents import AgentExecutor
from langchain.agents.agent_types import AgentType
from langchain.chat_models import ChatOpenAI

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
username = st.secrets["username"]
password = st.secrets["password"]
warehouse = st.secrets["warehouse"]
role = st.secrets["role"]
snowflake_account = st.secrets["account"]
database = st.secrets["database"]
schema = st.secrets["schema"]

def prepare_agent():
    snowflake_url = f"snowflake://{username}:{password}@{snowflake_account}/{database}/{schema}?warehouse={warehouse}&role={role}"
    db = SQLDatabase.from_uri(snowflake_url,sample_rows_in_table_info=1, include_tables=['merchant','my_me_merchant_benchmark','my_peer_merchant_benchmark','my_region_merchant_benchmark'])
    toolkit = SQLDatabaseToolkit(db=db, llm=OpenAI(temperature=0))
    
    #https://python.langchain.com/docs/integrations/toolkits/sql_database#using-zero_shot_react_description
    agent_executor = create_sql_agent(
        llm=OpenAI(temperature=0),
        toolkit=toolkit,
        use_query_checker=True,
        verbose=True,
        top_k=3,
        return_intermediate_steps=True,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    )
    
    st.session_state["agent_executor"] = agent_executor
    return agent_executor

#if 'agent_executor' not in st.session_state:
#    agent = prepare_agent()
agent = prepare_agent()

prompt = st.chat_input("How can I help you?")
if prompt:
    with st.spinner('Looking for answers...'):
        #agent = st.session_state["agent_executor"]
        answer = agent.run(prompt)
        with st.chat_message("assistant"):
            st.write("here is what I have found...")
            st.info(answer);
