from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.runnables import chain

template = \
"""You are an AI agent in a RAG (Retrieval-Augmented Generation) workflow.
Your job is to contextually compress the given document to a more concise version, contextually based on the user query and conversation summary, while retaining the most important information as accurately as possible.

Based on the query and conversation history, consider carefully the parts of the document to keep.

BACKGROUND DOCUMENT
Document metadata:
{metadata}

Document:
{background}
END OF BACKGROUND DOCUMENT

Conversation summary:
```{summary}```

You can return as a whole, or part of the document, as long as it is relevant to the user query and conversation history.
Remember: your task is to pick the important parts of the document and return those accurately. Most importantly is to NOT GENERATE NEW INFORMATION or make up details.
Do not include extraneous commentary, such as comments that the background document does not have the complete information or suggestions on where to find more information.

Return numbers, values, specific details, and other important information as accurately as possible."""


prompt = ChatPromptTemplate.from_messages(
    [
        ('system', template),
        ('human', 'Query: {question}')
    ]
)

@chain
def compressor_chain(_input: dict):
    question, doc, summary = _input['question'], _input['document'], _input['summary']
    _chain = prompt | ChatOpenAI(model='gpt-4o-mini', temperature=0) | StrOutputParser()
    response = _chain.invoke({'question': question, 'metadata': doc.metadata, 'background': doc.page_content, 'summary': summary})
    ret = {'compressed': response, 'metadata': doc.metadata}
    return ret