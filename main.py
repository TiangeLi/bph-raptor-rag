import os
import json
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
from st_utils import  StState

MAX_MSGS_IN_MEMORY = 10

load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv("LLM_APIKEY")

page_name = 'Chat BPH'
st.set_page_config(page_title=page_name)
st.title(page_name)

GPT_3 = 'gpt-3.5-turbo'
GPT_4 = 'gpt-4o'
llm = ChatOpenAI(model=GPT_4,temperature=0.7, max_tokens=2048, verbose=False)
summ = ChatOpenAI(model=GPT_3, temperature=0, max_tokens=512, verbose=False)
suggester = ChatOpenAI(model=GPT_3, temperature=1.0, max_tokens=256)

# ------------------------------------------------------------------- #
st_showbtns = StState('showbtns', default=True)

system_prompt = deque([SystemMessagePromptTemplate.from_template(template)])
summ_prompt = deque([HumanMessagePromptTemplate.from_template(summary_template)])
memm_prompt = deque([AIMessagePromptTemplate.from_template(memory_template)])

st_ui_msgs = StState('ui_msgs', default=[{"role": "ai", "content": AI_GREETING_MSG}])
st_llm_msgs = StState('llm_msgs', default=deque([AIMessage(content=AI_GREETING_MSG)], maxlen=MAX_MSGS_IN_MEMORY))
st_convo_summary = StState('convo_summary', default='(none so far. this is a brand new conversation.)')

st_prompt = StState('prompt', default='')

example_qs = [
        "What are the sexual side effects of TURP, Rezum, and Greenlight?",
        "Can you give a general overview on all the treatment options, focusing on retreatment risk?",
        "For a 55cc prostate, compare treatment options in a table in terms of catheter use and retention risk.",
        "Which treatments are suitable while remaining on anticoagulation therapy?"
    ]
st_generated_qs = StState('generated_qs', default=example_qs)

# ------------------------------------------------------------------- #

def assign_prompt(prompt):
    ss.prompt = prompt

for message in ss.ui_msgs:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if ss.showbtns:
    btns = st.empty()
    with btns.container():
        for q in ss.generated_qs:
            st.button(q, on_click=assign_prompt, args=(q,), use_container_width=True)


if prompt := st.chat_input(""):
    ss.prompt = ''
    if ss.showbtns:
        btns.empty()
        ss.showbtns = False

    ss.ui_msgs.append({"role": "user", "content": prompt})
    ss.llm_msgs.append(HumanMessage(content=prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("ai"):
        msgs = system_prompt+memm_prompt+ss.llm_msgs
        formated = ChatPromptTemplate.from_messages(msgs)
        stream = llm.stream(formated.format_prompt(context=text, summary=ss.convo_summary).to_messages())
        response = st.write_stream(stream)

        ss.ui_msgs.append({"role": "ai", "content": response})
        ss.llm_msgs.append(AIMessage(content=response))


    with st.spinner('Suggesting Questions...'):
        to_summ = ChatPromptTemplate.from_messages(memm_prompt+ss.llm_msgs+summ_prompt)
        print('----------------------')
        print(to_summ)
        print('----------------------')
        ss.convo_summary = summ(to_summ.format_prompt(summary=ss.convo_summary).to_messages())

        print('\n'*50)
        for i in msgs:
            print(i)
            print()
    
        btns = [st.empty(), st.empty(), st.empty()]
        q = "Given the context of the conversation so far: what 3 questions can I ask to further understand my options for BPH surgical treatments? "\
            "Return a JSON object in the form of \"q1\":\"question\", etc."
        msgs = system_prompt+memm_prompt+ss.llm_msgs+deque([HumanMessage(content=q)])
        msgs = ChatPromptTemplate.from_messages(msgs)
        qs = suggester(msgs.format_prompt(context=text, summary=ss.convo_summary).to_messages()).content
        qs = json.loads(qs)
        print()
        print()
        print(qs)
        ss.generated_qs = [qs[i] for i in qs]
        ss.showbtns = True
        st.rerun()

elif ss.prompt:
    prompt = ss.prompt
    ss.prompt = ''
    if ss.showbtns:
        btns.empty()
        ss.showbtns = False


    ss.ui_msgs.append({"role": "user", "content": prompt})
    ss.llm_msgs.append(HumanMessage(content=prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("ai"):
        msgs = system_prompt+memm_prompt+ss.llm_msgs
        formated = ChatPromptTemplate.from_messages(msgs)
        stream = llm.stream(formated.format_prompt(context=text, summary=ss.convo_summary).to_messages())
        response = st.write_stream(stream)

        ss.ui_msgs.append({"role": "ai", "content": response})
        ss.llm_msgs.append(AIMessage(content=response))

    with st.spinner('Suggesting Questions...'):
        to_summ = ChatPromptTemplate.from_messages(memm_prompt+ss.llm_msgs+summ_prompt)
        print('----------------------')
        print(to_summ)
        print('----------------------')
        ss.convo_summary = summ(to_summ.format_prompt(summary=ss.convo_summary).to_messages())



        print('\n'*50)
        for i in msgs:
            print(i)
            print()

        btns = [st.empty(), st.empty(), st.empty()]
        q = "Given the context of the conversation so far: what 3 questions can I ask to further understand my options for BPH surgical treatments? "\
            "Return a JSON object in the form of \"q1\":\"question\", etc."
        msgs = system_prompt+memm_prompt+ss.llm_msgs+deque([HumanMessage(content=q)])
        msgs = ChatPromptTemplate.from_messages(msgs)
        qs = suggester(msgs.format_prompt(context=text, summary=ss.convo_summary).to_messages()).content
        qs = json.loads(qs)
        print()
        print()
        print(qs)
        ss.generated_qs = [qs[i] for i in qs]
        ss.showbtns = True
        st.rerun()

print()
print()
print(ss.convo_summary)