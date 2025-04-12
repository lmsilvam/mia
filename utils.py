import streamlit as st
import glob
import os

def init_session_state(system_prompt):
    """Initializes required Streamlit session state variables."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": system_prompt}]

def load_system_prompt(file_path="prompt.txt"):
    """Loads the system prompt from a text file."""
    try:
        with open(file_path, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        st.error("¡No encontré instrucciones!")
        st.stop()

def load_papers():
    """Dynamically loads all paper*.txt files into memory."""
    papers = {}
    for paper_file in glob.glob("paper*.txt"):
        try:
            with open(paper_file, "r", encoding="utf-8") as file:
                papers[os.path.basename(paper_file)] = file.read()
        except Exception as e:
            st.warning(f"No se pudo cargar {paper_file}: {e}")
    return papers

def search_papers(query, papers):
    """Search for relevant excerpts in the papers."""
    results = []
    for title, content in papers.items():
        if query.lower() in content.lower():
            before, after = content.lower().split(query.lower(), 1)
            snippet = before[-300:] + query + after[:300]
            results.append(f"📄 {title}: ...{snippet}...")
    return results
