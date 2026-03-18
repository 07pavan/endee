import streamlit as st
from query import ask

st.set_page_config(page_title="Govt Scheme Copilot", layout="wide")

st.title("🇮🇳 Government Scheme AI Copilot")

st.write("Ask about Indian government schemes...")

# Session state for chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Input box
user_input = st.text_input("Ask your question:")

if st.button("Submit") and user_input:
    # Add user message
    st.session_state.messages.append(("user", user_input))

    # Get response
    response = ask(user_input)

    # Add bot message
    st.session_state.messages.append(("bot", response))

# Display chat
for role, message in st.session_state.messages:
    if role == "user":
        st.markdown(f"**🧑 You:** {message}")
    else:
        st.markdown(f"**🤖 AI:** {message}")