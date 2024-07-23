from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI

embd = OpenAIEmbeddings(model='text-embedding-3-large')

# app items
conv_llm = ChatOpenAI(model="gpt-4o", temperature=0.5)
summ_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, max_tokens=512)
sugg_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, max_tokens=256)