"""Streamlit frontend for RAG Document Q&A."""

import os
import time

import requests
import streamlit as st

# ========================
# Configuration
# ========================

DEFAULT_API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# ========================
# Page Config
# ========================

st.set_page_config(
    page_title="RAG Document Q&A",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Set API URL from sidebar
API_BASE_URL = st.sidebar.text_input(
    "API URL",
    value=DEFAULT_API_BASE_URL,
    key="api_url",
)

# ========================
# Helper Functions
# ========================


def api_request(method: str, endpoint: str, **kwargs) -> dict | None:
    """Make API request with error handling."""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        response = requests.request(method, url, timeout=120, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API. Is the server running?")
        return None
    except requests.exceptions.Timeout:
        st.error("⏳ Request timed out. The model might be loading.")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ API Error: {e.response.text}")
        return None


def check_health() -> bool:
    """Check if API is healthy."""
    result = api_request("GET", "/health")
    return result is not None and result.get("status") == "healthy"


def get_stats() -> dict | None:
    """Get document statistics."""
    return api_request("GET", "/documents/stats")


def ingest_text(text: str, title: str) -> dict | None:
    """Ingest text into the system."""
    return api_request(
        "POST",
        "/documents/ingest-text",
        json={"text": text, "title": title},
    )


def upload_file(file, title: str) -> dict | None:
    """Upload a file to the system."""
    return api_request(
        "POST",
        "/documents/upload",
        files={"file": (file.name, file.getvalue(), file.type)},
        data={"title": title},
    )


def query_documents(question: str, k: int = 3) -> dict | None:
    """Query the RAG system."""
    return api_request(
        "POST",
        "/query",
        json={"question": question, "k": k, "include_sources": True},
    )


def clear_documents() -> dict | None:
    """Clear all documents."""
    return api_request("DELETE", "/documents/clear")


# ========================
# Sidebar
# ========================

with st.sidebar:
    st.title("🤖 RAG Document Q&A")
    st.markdown("---")

    # Health Status
    st.subheader("🔗 API Status")
    if check_health():
        st.success("✅ API Connected")
    else:
        st.error("❌ API Disconnected")
        st.info("Start the API server first:\n```\nmake run\n```")

    st.markdown("---")

    # Document Stats
    st.subheader("📊 Document Stats")
    stats = get_stats()
    if stats:
        col1, col2 = st.columns(2)
        col1.metric("Documents", stats.get("document_count", 0))
        col2.metric("Collection", stats.get("collection_name", "N/A"))
    else:
        st.info("No stats available")

    st.markdown("---")

    # Clear Documents
    st.subheader("🗑️ Management")
    if st.button("Clear All Documents", type="secondary", use_container_width=True):
        result = clear_documents()
        if result:
            st.success("All documents cleared!")
            st.rerun()

    st.markdown("---")
    st.markdown(
        "**Built by [M. Nusrat Ullah](https://github.com/M-Nusrat-Ullah)**"
    )

# ========================
# Main Content
# ========================

st.title("🤖 RAG Document Q&A")
st.caption("Upload documents and ask questions powered by AI")

# Tabs
tab_qa, tab_upload, tab_text = st.tabs(
    ["💬 Ask Questions", "📄 Upload Document", "📝 Ingest Text"]
)

# ========================
# Tab 1: Q&A
# ========================

with tab_qa:
    st.subheader("Ask a Question")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("sources"):
                with st.expander("📚 Sources"):
                    for i, source in enumerate(message["sources"]):
                        st.markdown(
                            f"**Source {i+1}** "
                            f"(relevance: {source.get('relevance_score', 'N/A')})"
                        )
                        st.caption(source.get("content", ""))
                        st.markdown("---")

    # Chat input
    question = st.chat_input("Ask a question about your documents...")

    if question:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                start_time = time.time()
                result = query_documents(question, k=3)
                elapsed = time.time() - start_time

            if result:
                answer = result.get("answer", "No answer generated.")
                sources = result.get("sources", [])
                model = result.get("model_used", "unknown")

                st.markdown(answer)
                st.caption(f"⏱️ {elapsed:.1f}s | 🤖 {model}")

                if sources:
                    with st.expander("📚 Sources"):
                        for i, source in enumerate(sources):
                            st.markdown(
                                f"**Source {i+1}** "
                                f"(relevance: {source.get('relevance_score', 'N/A')})"
                            )
                            st.caption(source.get("content", ""))
                            st.markdown("---")

                # Save to history
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                    }
                )
            else:
                st.error("Failed to get a response. Check API connection.")

    # Empty state
    if not st.session_state.messages:
        st.info(
            "👋 Upload some documents first, then ask questions here!\n\n"
            "Try: *'What is this document about?'*"
        )

# ========================
# Tab 2: File Upload
# ========================

with tab_upload:
    st.subheader("Upload a Document")
    st.caption("Supported formats: PDF, TXT, MD")

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["pdf", "txt", "md"],
        help="Upload a PDF, TXT, or Markdown file",
    )

    file_title = st.text_input(
        "Document Title (optional)",
        placeholder="e.g., Company Policy Manual",
        key="file_title",
    )

    if st.button("📤 Upload & Process", type="primary", disabled=not uploaded_file):
        if uploaded_file:
            with st.spinner(f"Processing {uploaded_file.name}..."):
                result = upload_file(
                    uploaded_file, file_title or uploaded_file.name
                )

            if result:
                st.success(
                    f"✅ **{uploaded_file.name}** uploaded successfully!\n\n"
                    f"- Chunks created: **{result.get('chunks_created', 0)}**\n"
                    f"- Total documents: **{result.get('total_documents', 0)}**"
                )
                st.balloons()
            else:
                st.error("Failed to upload document.")

# ========================
# Tab 3: Text Ingestion
# ========================

with tab_text:
    st.subheader("Ingest Raw Text")
    st.caption("Paste any text content to add to the knowledge base")

    text_title = st.text_input(
        "Title",
        placeholder="e.g., Meeting Notes - Q4 Review",
        key="text_title",
    )

    text_content = st.text_area(
        "Text Content",
        placeholder="Paste your text here...",
        height=200,
        key="text_content",
    )

    if st.button(
        "📥 Ingest Text",
        type="primary",
        disabled=not text_content,
    ):
        if text_content:
            with st.spinner("Processing text..."):
                result = ingest_text(
                    text_content, text_title or "Direct Text Input"
                )

            if result:
                st.success(
                    f"✅ Text ingested successfully!\n\n"
                    f"- Chunks created: **{result.get('chunks_created', 0)}**\n"
                    f"- Total documents: **{result.get('total_documents', 0)}**"
                )
                st.balloons()
            else:
                st.error("Failed to ingest text.")