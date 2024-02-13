import os
from dotenv import load_dotenv

from collections import deque

import streamlit as st
from streamlit import session_state as ss

from langchain_openai import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate, AIMessagePromptTemplate
)
from langchain.schema import AIMessage, HumanMessage

from template import template, text, summary_template, memory_template, AI_GREETING_MSG

load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv("LLM_APIKEY")
page_name = 'Chat BPH'
GPT_3 = 'gpt-3.5-turbo-0125'
GPT_4 = 'gpt-4-turbo-preview'
llm = ChatOpenAI(model=GPT_3,temperature=0.6, max_tokens=2048, verbose=False)
summ = ChatOpenAI(model=GPT_3, temperature=0, max_tokens=512, verbose=False)

# ------------------------------------------------------------------- #

system_prompt = SystemMessagePromptTemplate.from_template(template)
summ_prompt = deque([HumanMessagePromptTemplate.from_template(summary_template)])
memm_prompt = deque([AIMessagePromptTemplate.from_template(memory_template)])

if "messages" not in st.session_state:
    ss.messages = [{"role": "ai", "content": AI_GREETING_MSG}]

if "llm_messages" not in st.session_state:
    ss.llm_messages = deque([AIMessage(content=AI_GREETING_MSG)], maxlen=10)
system_prompt = deque([system_prompt])

if "summary" not in st.session_state:
    ss.summary = '(none so far. this is a brand new conversation.)'

# ------------------------------------------------------------------- #

st.set_page_config(page_title=page_name)
st.title(page_name)

for message in ss.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input(""):
    ss.messages.append({"role": "user", "content": prompt})
    ss.llm_messages.append(HumanMessage(content=prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("ai"):
        msgs = system_prompt+memm_prompt+ss.llm_messages
        formated = ChatPromptTemplate.from_messages(msgs)
        stream = llm.stream(formated.format_prompt(context=text, summary=ss.summary).to_messages())
        response = st.write_stream(stream)

        ss.messages.append({"role": "ai", "content": response})
        ss.llm_messages.append(AIMessage(content=response))


        to_summ = ChatPromptTemplate.from_messages(memm_prompt+ss.llm_messages+summ_prompt)
        print('----------------------')
        print(to_summ)
        print('----------------------')
        ss.summary = summ(to_summ.format_prompt(summary=ss.summary).to_messages())

    



        print('\n'*50)
        for i in msgs:
            print(i)
            print()

print()
print()
print(ss.summary)