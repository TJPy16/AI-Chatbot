#Main App File
import streamlit as st
import openai
import os
import PyPDF2
from dotenv import load_dotenv

openai.api_key = st.secret["OPENAI_API_KEY"]
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

role = st.selectbox('Choose your assistant role:', ['Career Coach', 'Health Advisor'])
if not st.session_state.chat_history:
    if role == "Career Coach":
        system_msg = "You are a career advisor who helps users write better resumes."
    elif role == "Health Advisor":
        system_msg = "You are a health advisor who gives personalized health and wellness tips."

    st.session_state.chat_history.append({"role": "system", "content": system_msg})

for msg in st.session_state.chat_history:
    st.write(f"**{msg['role'].capitalize()}**: {msg['content']}")

user_upload = st.file_uploader("Upload a File:", type='pdf')
if user_upload and 'pdf_file' not in st.session_state:
    reader = PyPDF2.PdfReader(user_upload)
    pdf_file = ""
    for page in reader.pages:
        pdf_file += page.extract_text()
    st.session_state['pdf_file'] = pdf_file

user_input = st.text_input("Ask Anything:")

if st.button('Enter') and user_input:
    st.session_state.chat_history.append({'role': 'user', 'content': user_input})

    messages_to_send = st.session_state.chat_history.copy()

    if 'pdf_file' in st.session_state:
        messages_to_send.insert(1, {
            "role": "user",
            "content": "Here is some context from a document:\n" + st.session_state['pdf_file']
        })

    reply = openai.ChatCompletion.create(
        model = 'gpt-3.5-turbo',
        messages = messages_to_send
    )
    assistant_reply = reply['choices'][0]['message']['content']
    st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
    st.write(f"**Assistant**: {assistant_reply}")


#In Prompt Evaluation Mode:
mode = st.radio('Choose Mode:', ['Chatbot', 'Prompt Evaluation'])
question = st.text_input('Enter your question:')
if mode == 'Chatbot':
    prompt_A = 'You are a helpful general-purpose assistant.'
    prompt_B = 'You are a career coach who gives confident, motivating answers.'
    messages_A = [
        {"role": "system", "content": prompt_A},
        {"role": "user", "content": question}
    ]
    messages_B = [
        {"role": "system", "content": prompt_B},
        {"role": "user", "content": question}
    ]

    response_A = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages_A
    )

    response_B = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages_B
    )

col1, col2 = st.columns(2)
with col1:
    st.subheader('Prompt A')
    st.write(response_A['choices'][0]['message']['content'])
with col2:
    st.subheader('Prompt B')
    st.write(response_B['choices'][0]['message']['content'])

vote = st.radio('Which response is better?', ['Prompt A', 'Prompt B'])

if 'votes' not in st.session_state:
    st.session_state.votes = []
if vote:
    st.session_state.votes.append({
        "question": question,
        "vote": vote
    })

if st.button("Reset Chat"):
    st.session_state.chat_history = []
    if "pdf_file" in st.session_state:
        del st.session_state["pdf_file"]