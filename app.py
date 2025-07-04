import streamlit as st
from document_processor import DocumentProcessor
from vector_store import VectorStore
from chatbot import BWTSChatbot
from dotenv import load_dotenv
load_dotenv()

import os
print("🔑 Key loaded in app.py:", os.getenv("GROQ_API_KEY"))


# Page config
st.set_page_config(
    page_title="BWTS Technical Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize classes
doc_processor = DocumentProcessor()
vector_store = VectorStore()
chatbot = BWTSChatbot()

# Session state setup
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'documents_loaded' not in st.session_state:
    st.session_state.documents_loaded = False

# Header
st.markdown("""
    <h1 style='text-align:center; color:#1e3a8a;'>🚢 BWTS Technical Assistant</h1>
    <p style='text-align:center;'>AI-Powered Chatbot for Ballast Water Treatment System Manuals</p>
""", unsafe_allow_html=True)

# Sidebar: Upload PDFs
with st.sidebar:
    st.header("📁 Upload BWTS PDFs")
    uploaded_files = st.file_uploader("Upload PDFs", type=['pdf'], accept_multiple_files=True)

    if uploaded_files and st.button("📄 Process Documents"):
        with st.spinner("Processing PDFs..."):
            chunks = doc_processor.process_pdfs(uploaded_files)
            vector_store.add_documents(chunks)
            st.session_state.documents_loaded = True
        st.success("Documents processed and stored successfully!")

    if st.session_state.documents_loaded:
        stats = vector_store.get_collection_stats()
        st.metric("Documents in Vector DB", stats['total_documents'])

    st.divider()
    st.header("⚙ Filter Options")
    doc_type_filter = st.selectbox("Document Type", ['all', 'operational', 'maintenance', 'troubleshooting', 'regulatory'])
    num_sources = st.slider("Number of Sources to Retrieve", 1, 10, 5)

# Chat UI
st.header("💬 Ask a Question About BWTS")
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask something like 'How often to replace UV lamp?'"):
    if not st.session_state.documents_loaded:
        st.error("❗ Please upload and process PDFs first.")
    else:
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response, sources = chatbot.answer_query(prompt)
                st.markdown(response)

                if sources:
                    with st.expander("📚 Sources"):
                        for i, doc in enumerate(sources, 1):
                            st.markdown(f"""
                                **Source {i}**
                                • **File**: *{doc['source']}*
                                • **Page**: {doc['page']}
                                • **Type**: {doc['doc_type']}
                            """)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "sources": sources
                })
