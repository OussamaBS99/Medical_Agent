import streamlit as st
from backend.agent import Agent
import requests
import time
import re
from copy import deepcopy
BACKEND_URL = "http://127.0.0.1:8000/"

def reply(message):
    # Send message to backend
    try:
        res = requests.post(BACKEND_URL+"chat", json={"message": message})
        return res.json().get("response", "⚠️ No reply from backend")
    except Exception as e:
        return f"❌ Backend error: {str(e)}"
    
def summerize(message):
    # Send message to backend
    try:
        res = requests.post(BACKEND_URL+"summerize", json={"message": message})
        return res.json().get("response", "⚠️ No reply from backend")
    except Exception as e:
        return f"❌ Backend error: {str(e)}"

def generate_audio(message: str):
    """
    Sends a message to the backend /audio endpoint and returns audio bytes.
    """
    res = requests.post(
        BACKEND_URL + "audio",
        json={"message": message},
    )
    return res.content




def upload(files):
    res=requests.post(BACKEND_URL+"upload", files=files)

st.set_page_config(page_title="💬 Multi-Chat Bot", layout="wide")

# Initialize session state for conversations
if "conversations" not in st.session_state:
    st.session_state.conversations = {"New Conversation":[]}  # {conv_name: [messages]}
if "current_conv" not in st.session_state:
    st.session_state.current_conv = "New Conversation"
# Sidebar
with st.sidebar:
        # --- 🧩 Integrated File Upload Area ---
    st.title("Attach Files")
    uploaded_files = st.file_uploader(
        label="Upload files",        # label is required but we’ll hide it
        type=["txt", "pdf", "csv", "docx"],
        accept_multiple_files=True,
        label_visibility="collapsed"  # ✅ completely hides the label
    )

    # Process uploaded files
    files = [("files", (f.name, f, f.type)) for f in uploaded_files]
    if files:
        upload(files)

    st.title("Chats")
    
    #   New conversation button
    if st.button("✚ New Conversation", use_container_width=True):
        if st.session_state.current_conv == "New Conversation" and st.session_state.conversations["New Conversation"] != []:
            m = deepcopy(st.session_state.conversations.get(st.session_state.current_conv, []))
            conv_topic=summerize(m)
            st.session_state.conversations[conv_topic] = st.session_state.conversations[st.session_state.current_conv]
        st.session_state.conversations["New Conversation"] = []
        st.session_state.current_conv = "New Conversation"
        st.rerun()  # ✅ reruns safely (no 'experimental' prefix anymore)

    # Scrollable list of conversation buttons
    with st.container():
        # Add vertical scroll
        st.markdown(
            """
            <style>
            .scroll-container {
                max-height: 350px;
                overflow-y: auto;
                padding-right: 5px;
            }
            .conv-button {
                width: 100%;
                text-align: left;
                background-color: #262730;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 0.5em;
                margin-bottom: 0.3em;
                cursor: pointer;
            }
            .conv-button:hover {
                background-color: #383a45;
            }
            .active {
                background-color: #565869;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="scroll-container">', unsafe_allow_html=True)

        # Render one button per conversation
        for name in list([x for x  in st.session_state.conversations.keys() if x!="New Conversation"])[::-1]:
            is_active = name == st.session_state.current_conv
            button_html = f"""
            <form action="#" method="post">
                <button class="conv-button {'active' if is_active else ''}" name="conv" type="submit">{name}</button>
            </form>
            """
            if st.button(name, key=name, use_container_width=True):
                st.session_state.current_conv = name
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
# Main chat area
st.title(f"Chat")

# Get current messages
messages = st.session_state.conversations.get(st.session_state.current_conv, [])

# Display previous messages
for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask me anything"):
    # User message
    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant response
    response = reply(messages)
    with st.chat_message("assistant"):
        st.markdown(response)
    messages.append({"role": "assistant", "content": response})

# Save back to session state
st.session_state.conversations[st.session_state.current_conv] = messages
