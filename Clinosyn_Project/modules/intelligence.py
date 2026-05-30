import streamlit as st
import time
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_ollama import ChatOllama
from modules.db_utils import DB_PATH

def render_intelligence():
    st.title("🧠 Clinical Intelligence (RAG)")
    st.markdown("Ask natural language questions about OmniIngest clinical data (e.g., 'How many patients have high bills?').\n\n🛡️ **Powered securely by local offline AI (Ollama)** - Zero data leaves this device.")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    query = st.chat_input("Ask a clinical question...")

    if query:
        st.chat_message("user").markdown(query)
        st.session_state.messages.append({"role": "user", "content": query})

        with st.chat_message("assistant"):
            with st.spinner("Analyzing Clinical Data locally with Llama3..."):
                try:
                    # 1. Setup LangChain SQL Agent with Ollama
                    db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")
                    llm = ChatOllama(model="llama3", temperature=0)
                    
                    agent_executor = create_sql_agent(
                        llm=llm,
                        db=db,
                        verbose=True,
                        handle_parsing_errors=True
                    )
                    
                    # 2. Inject strict clinical prompt
                    prompt = f"""
                    You are Clinosyn, an advanced clinical OS and medical AI. 
                    Query the SQLite database to answer the user's question.
                    If asked to check prescriptions against allergies, carefully examine the clinical_payload column.
                    User Question: {query}
                    """
                    
                    response = agent_executor.invoke({"input": prompt})["output"]
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                except Exception as e:
                    error_msg = f"⚠️ Ollama Error: Is Ollama installed and running? Did you download the 'llama3' model? (Details: {str(e)})"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
