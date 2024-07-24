from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI

EMBD = OpenAIEmbeddings(model='text-embedding-3-large')


# ------------------------------------------------------------------- #
# we go in such painful granularity on the models,
# to future proof easy model swapping on each function
# Obviously doesn't matter right now

# MAIN
CONVLLM = ChatOpenAI(model="gpt-4o", temperature=0.5)
SUMMLLM = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Doc Filter
FILTLLM = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Router
ROUTERLLM = ChatOpenAI(model='gpt-4o-mini', temperature=0)

# Algo Reader
ALGOLLM = ChatOpenAI(model='gpt-4o-mini', temperature=0)

# Contextual compressor
COMPRESSORLLM = ChatOpenAI(model='gpt-4o-mini', temperature=0) 

# Multi query generator
MULTIQUERYLLM = ChatOpenAI(model='gpt-4o', temperature=0)
REPHRASINGLLM = ChatOpenAI(model='gpt-4o', temperature=0)
REORGLLM = ChatOpenAI(model='gpt-4o-mini', temperature=0)