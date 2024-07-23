import os
import json
from dotenv import load_dotenv
load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_APIKEY")
os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_APIKEY")
os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ['LANGCHAIN_API_KEY'] = os.getenv('LS_APIKEY')
os.environ['LANGCHAIN_ENDPOINT'] = 'https://api.smith.langchain.com'
os.environ['LANGCHAIN_PROJECT'] = 'bph-gpt-raptor'

from collections import deque

import streamlit as st
from streamlit import session_state as ss

from langchain_openai import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate, AIMessagePromptTemplate
)
from langchain.schema import AIMessage, HumanMessage, SystemMessage

from template import template, summary_template, memory_template, AI_GREETING_MSG, surg_abbrevs_table
from st_utils import  StState

from multiretriever import generate_queries, reciprocal_rank_fusion
from routingagent import router_chain
from algoreader import tx_algo_chain, aua_surg_algo, cua_surg_algo, eau_surg_algo
from constants import conv_llm, summ_llm, sugg_llm, embd
from llm_doc_filter import doc_filter_chain
from contextual_compressor import compressor_chain

# sources sorting function
def custom_sort_key(item):
    # Provide a default value (e.g., float('inf')) for missing keys
    return (
        item.get('Title', 'NO_KEY'),
        item.get('Header 1', 'NO_KEY'),
        item.get('Header 2', 'NO_KEY'),
        item.get('Header 3', 'NO_KEY'),
        item.get('Header 4', 'NO_KEY'),
        item.get('Header 5', 'NO_KEY')
    )

# ------------------------------------------------------------------- #
import pickle
from langchain.storage import InMemoryByteStore
from langchain_community.vectorstores import FAISS  
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.retrievers.multi_vector import SearchType


# note: the guideline documents are saved as and loaded from pkl files, but not generated in this repo
# currenly they're being generated in RAG_BPH/md_test.ipynb, using cua.md, aua.md, and eau.md
# documents include raw segmented chunks (by markdown headers) and RAPTOR recursive summaries for each guideline
# guidelines are generated from parsed pdfs and manually cleaned up prior to chunking and summarization

def get_retriever(pickle_directory, top_k=3):
    with open(f'pkl/{pickle_directory}/doc_ids.pkl', 'rb') as file:
        doc_ids = pickle.load(file)
    with open(f'pkl/{pickle_directory}/summary_docs.pkl', 'rb') as file:
        summary_docs = pickle.load(file)
    with open(f'pkl/{pickle_directory}/docs.pkl', 'rb') as file:
        docs = pickle.load(file)

    vectorstore = FAISS.from_documents(summary_docs, embd)
    store = InMemoryByteStore()
    id_key = 'doc_id'
    retriever = MultiVectorRetriever(
        vectorstore=vectorstore,
        byte_store=store,
        id_key=id_key,
        search_type=SearchType.similarity,
        search_kwargs={'k': top_k}
    )
    retriever.docstore.mset(list(zip(doc_ids, docs)))
    return retriever

cua_retreiver = get_retriever('cua')
aua_retreiver = get_retriever('aua')
eau_retreiver = get_retriever('eau')

# ------------------------------------------------------------------- #

MAX_MSGS_IN_MEMORY = 10

page_name = 'Chat BPH'
st.set_page_config(page_title=page_name)
st.title(page_name)

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
        "For a 55cc prostate, compare surgical options in a table in terms of catheter use and retention risk.",
        "Which treatments are suitable while remaining on anticoagulation?",
        "Which treatment is best if I want to preserve sexual function?"
    ]
st_generated_qs = StState('generated_qs', default=example_qs)

# ------------------------------------------------------------------- #

def assign_prompt(prompt):
    ss.prompt = prompt

for message in ss.ui_msgs:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
    if message.get('sources', None):
        if message['sources'] != 'n/a':
            with st.expander('Sources'):
                st.caption(message['sources'])
        else:
            st.caption('Sources: n/a')

if ss.showbtns:
    btns = st.empty()
    with btns.container():
        for q in ss.generated_qs:
            st.button(q, on_click=assign_prompt, args=(q,), use_container_width=True)


if prompt := st.chat_input("") or ss.prompt:
    prompt = ss.prompt or prompt
    prompt = prompt.strip()
    ss.ui_msgs.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    

    ss.prompt = ''
    if ss.showbtns:
        btns.empty()
        ss.showbtns = False


    with st.chat_message("ai"):
        
        with st.status('Reading Guidelines...', expanded=True) as status:

            st.write('Generating Topic Expansion...')
            algos = [aua_surg_algo, cua_surg_algo, eau_surg_algo]
            names = ['AUA', 'CUA', 'EAU']
            algos = [{'question': prompt, 'algo': algo, 'summary':ss.convo_summary} for algo in algos]
            tx_options = [b.lower().strip() for b in tx_algo_chain.batch(algos)]

            relevant_tx = []
            for i,algo in enumerate(names):
                if tx_options[i] != 'none': relevant_tx.append(f'[{tx_options[i].upper()}] according to the {algo} Guidelines')
            
            if len(relevant_tx) > 0:
                relevant_tx_str = ', and '.join(relevant_tx)
                relevant_tx_str = f'Based on my query, the recommended surgical therapies based on guideline algorithms are {relevant_tx_str}.\
                    \n\nProvide a very succinct summary at the start to highlight which treatments are recommended by which guideline.\n\
                    Since different guidelines use different terms to refer to the same treatment, try to unify them using this reference table:\n\n\
                    {surg_abbrevs_table}\n\n\
                    Then, discuss in more detail the treatments relevant to my exact query above.\n\n'
            else:
                relevant_tx_str = ''
            
            guiding_prompt = SystemMessage(content=f'{relevant_tx_str}\
                                           You should give a brief overview of the differences between the guidelines at the start of your response. \
                                           \nYou should try to combine the information from each guideline where possible, highlighting only major differences as you go, if applicable.')

            routed = router_chain.invoke({"question":prompt, 'summary': ss.convo_summary}).lower().strip()
            if routed == 'no' and all(i == 'none' for i in tx_options):
                context = 'n/a'
                ret = None
                queries_dict = {'rephrased': prompt, 'original': prompt}  # no changes or query expansion. 
            else:  # routed == 'yes' or routed == any other string or tx_options is present; we treat it as 'yes'
                question = prompt+'\n\n'+'discuss '+f'{[i for i in tx_options]}'+'\n\n'+ss.convo_summary
                queries_dict = generate_queries.invoke(question)

                st.dataframe({k:v for k, v in queries_dict.items() if k != 'original'})

                st.write('Retrieving Documents...')
                queries_list = [q for q in queries_dict.values() if q]
                cua_ret = (cua_retreiver.map() | reciprocal_rank_fusion).invoke(queries_list)
                aua_ret = (aua_retreiver.map() | reciprocal_rank_fusion).invoke(queries_list)
                eau_ret = (eau_retreiver.map() | reciprocal_rank_fusion).invoke(queries_list)
                ret = reciprocal_rank_fusion([cua_ret, aua_ret, eau_ret])
                print(len(ret))

                st.write('Compressing and Synthesizing Query...')
                filtered_ret = doc_filter_chain.map().invoke([{
                    'document': r,
                    'queries_dict': queries_dict}
                    for r in ret])
                ret = [f for f in filtered_ret if f.page_content]# [r for r, f in zip(ret, filtered_ret) if f.lower().strip() == 'yes']
                print(len(ret))


                compressed = [{'compressed': doc.page_content, 'metadata': doc.metadata} for doc in ret]  # we're not actually compressing here, just passing through. TODO: remove.
                #compressed = compressor_chain.map().invoke([{ 'question': queries_dict['rephrased'], 'document': r, 'summary': ss.convo_summary} for r in ret])
                c = [f'```Document #{i+1}\nSOURCE: {r['metadata'].get('Title', r['metadata'])}\n\n{r['compressed']}```' for i, r in enumerate(compressed)]
                context = "\n\n".join(c)

            print('\n', routed, tx_options, len(ret) if ret else 0, len([r for r in ret if r.metadata.get('Header 1')]) if ret else 0, '\n')

            status.update(label='Complete!', state='complete', expanded=False)


        msgs = system_prompt+memm_prompt+ss.llm_msgs
        msgs.append(guiding_prompt)
        msgs.append(HumanMessage(content=queries_dict['rephrased']))
        formated = ChatPromptTemplate.from_messages(msgs)

        ss.llm_msgs.append(HumanMessage(content=prompt))
        
        stream = conv_llm.stream(formated.format_prompt(context=context, summary=ss.convo_summary).to_messages())
        response = st.write_stream(stream)

        #ss.ui_msgs.append({"role": "ai", "content": response})
        ss.llm_msgs.append(AIMessage(content=response))


    with st.spinner('Getting Sources...'):
        to_summ = ChatPromptTemplate.from_messages(memm_prompt+ss.llm_msgs+summ_prompt)
        ss.convo_summary = summ_llm(to_summ.format_prompt(summary=ss.convo_summary).to_messages()).content

        if ret:
            sources = [r.metadata for r in ret if r.metadata.get('Header 1')]
            sources_sorted = sources # sorted(sources, key=custom_sort_key)    # sorting by metadata key is disabled for now, sorted by reciprocal rank fusion
            final_sources = []
            for i, r in enumerate(sources_sorted):
                guideline = r['Title']
                if 'AUA' in guideline: guideline = 'AUA Guidelines'
                elif 'EAU' in guideline: guideline = 'EAU Guidelines'
                elif 'CUA' in guideline: guideline = 'CUA Guidelines'
                else: guideline = ''
                formatted_string = f'{guideline} | ' + "".join([f"{value.strip('*')} | " for key, value in r.items() if key != 'Title'])
                final_sources.append(f'{i+1}. | {formatted_string}')

            raptor_num_tracker = {}
            raptor_sources = [r.metadata for r in ret if not r.metadata.get('Header 1')]
            for r in raptor_sources:
                guideline = r['Title']
                if 'AUA' in guideline: guideline = 'AUA Guidelines'
                elif 'EAU' in guideline: guideline = 'EAU Guidelines'
                elif 'CUA' in guideline: guideline = 'CUA Guidelines'
                else: guideline = ''
                raptor_num_tracker[guideline] = raptor_num_tracker.get(guideline, 0) + 1
            raptor_num_str = ' | '.join([f'{k}: {v}' for k,v in raptor_num_tracker.items()])

            final_sources_str = f'{"\n".join(final_sources)}\n\nRAPTOR Documents: {raptor_num_str}'
        else:
            final_sources_str = 'n/a'

        
        ss.ui_msgs.append({"role": "ai", "content": response, 'sources': final_sources_str})
        if final_sources_str != 'n/a':
            with st.expander('Sources'):
                st.caption(final_sources_str)
        else:
            st.caption('Sources: n/a')


    

        while generate_qs := False:
            btns = [st.empty(), st.empty(), st.empty()]
            q = "Given the context of the conversation so far: what 3 questions can I ask to further understand my options for BPH surgical treatments? "\
                "Return just a JSON object in exactly this template: \n\n{\n  \"q1\": ...,\n   etc.\n}"
            msgs = system_prompt+memm_prompt+ss.llm_msgs+deque([HumanMessage(content=q)])
            msgs = ChatPromptTemplate.from_messages(msgs)
            qs = sugg_llm(msgs.format_prompt(context=context, summary=ss.convo_summary).to_messages()).content
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