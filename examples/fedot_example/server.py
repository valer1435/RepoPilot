import requests
import streamlit as st
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from fedot_example import rag_app

load_dotenv()


def get_page_title(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad responses (4xx, 5xx)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string
        return title
    except requests.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None


st.title("RepoCopilot assistant")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history

    st.session_state.messages.append({"role": "user", "content": prompt})

    response, citations = rag_app.query(prompt, citations=True)
    # Display assistant response in chat message container
    sources = list(set([get_page_title(i[1]['url']) + ': ' + i[1]['url'] for c, i in enumerate(citations)]))
    listed_sources = []
    for i, s in enumerate(sources):
        listed_sources.append(f'{i+1}. {s}')
    final_response = '\n'.join([response, '\n*I used this source docs for the answer:*'] + listed_sources)
    with st.chat_message("assistant"):
        st.markdown(final_response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": final_response})
